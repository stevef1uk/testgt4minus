import { test, expect, type APIRequestContext, type Page } from "@playwright/test";

const pName = (label: string) =>
  `PW ${label} ${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

async function cleanup(request: APIRequestContext, name: string): Promise<void> {
  const r = await request.get("/api/projects");
  if (!r.ok()) return;
  for (const p of (await r.json()) as Array<{ id: number; name: string }>) {
    if (p.name === name) await request.delete(`/api/projects/${p.id}`);
  }
}

async function addProject(page: Page, name: string): Promise<void> {
  await page.locator("#project-name").fill(name);
  await page.getByRole("button", { name: "Add project" }).click();
  await expect(page.locator("#task-panel")).toBeVisible();
}

async function addTask(page: Page, title: string, priority: string): Promise<void> {
  await page.locator("#task-title").fill(title);
  await page.locator("#task-priority").selectOption(priority);
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(page.locator("#todo-list").getByText(title, { exact: true })).toBeVisible();
}

test("first load displays the TaskBoard and all Kanban columns", async ({ page, request }) => {
  const name = pName("load");
  await request.post("/api/projects", { data: { name } });
  try {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "TaskBoard", exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "To Do", exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Doing", exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Done", exact: true })).toBeVisible();
  } finally {
    await cleanup(request, name);
  }
});

test("creates, moves, and deletes a task through the browser", async ({ page, request }) => {
  const name = pName("workflow");
  try {
    await page.goto("/");
    await addProject(page, name);
    await addTask(page, "Release browser workflow", "medium");
    const todo = page.locator("#todo-list");
    await todo.getByRole("button", { name: "Move forward" }).click();
    const doing = page.locator("#doing-list");
    await expect(doing.getByText("Release browser workflow", { exact: true })).toBeVisible();
    await doing.getByRole("button", { name: "Move forward" }).click();
    const done = page.locator("#done-list");
    await expect(done.getByText("Release browser workflow", { exact: true })).toBeVisible();
    await expect(done.getByRole("button", { name: "Move forward" })).toHaveCount(0);
    await done.getByRole("button", { name: "Delete" }).click();
    await expect(done.getByText("Release browser workflow", { exact: true })).toHaveCount(0);
  } finally {
    await cleanup(request, name);
  }
});

test("filters tasks by priority and restores the full list", async ({ page, request }) => {
  const name = pName("filters");
  try {
    await page.goto("/");
    await addProject(page, name);
    await addTask(page, "High priority task", "high");
    await addTask(page, "Low priority task", "low");
    await page.locator("#priority-filter").selectOption("high");
    await expect(page.getByText("High priority task", { exact: true })).toBeVisible();
    await expect(page.getByText("Low priority task", { exact: true })).toHaveCount(0);
    await page.locator("#priority-filter").selectOption("all");
    await expect(page.getByText("Low priority task", { exact: true })).toBeVisible();
  } finally {
    await cleanup(request, name);
  }
});