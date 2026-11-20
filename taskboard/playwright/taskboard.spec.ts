import { test, expect, type APIRequestContext, type Page } from "@playwright/test";

const projectName = (label: string) =>
  `Playwright ${label} ${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

async function removeProject(
  request: APIRequestContext,
  name: string,
): Promise<void> {
  const response = await request.get("/api/projects");
  if (!response.ok()) return;

  const projects = (await response.json()) as Array<{ id: number; name: string }>;
  for (const project of projects.filter((item) => item.name === name)) {
    await request.delete(`/api/projects/${project.id}`);
  }
}

async function createProjectFromUI(page: Page, name: string): Promise<void> {
  await page.getByRole("button", { name: "New project" }).click();
  await page.getByLabel("Name").fill(name);
  await page.getByRole("button", { name: "Save project" }).click();
  await expect(page.getByText(name, { exact: true })).toBeVisible();
  await page.getByText(name, { exact: true }).click();
}

test.beforeEach(async ({ request }) => {
  const response = await request.get("/api/projects");
  if (!response.ok()) return;

  const projects = (await response.json()) as Array<{ id: number }>;
  for (const project of projects) {
    await request.delete(`/api/projects/${project.id}`);
  }
});

test("first load displays the TaskBoard and all Kanban columns", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "TaskBoard", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "To Do", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Doing", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Done", exact: true })).toBeVisible();
});

test("creates, moves, and deletes a task through the browser", async ({
  page,
  request,
}) => {
  const name = projectName("workflow");
  try {
    await page.goto("/");
    await createProjectFromUI(page, name);

    await page.getByRole("button", { name: "New task" }).click();
    await page.getByLabel("Task title").fill("Release browser workflow");
    await page.getByRole("button", { name: "Save task" }).click();

    const todo = page.locator("#todo-tasks");
    await expect(todo.getByText("Release browser workflow", { exact: true })).toBeVisible();

    await todo.getByRole("button", { name: "Move forward" }).click();
    const doing = page.locator("#doing-tasks");
    await expect(doing.getByText("Release browser workflow", { exact: true })).toBeVisible();

    await doing.getByRole("button", { name: "Move forward" }).click();
    const done = page.locator("#done-tasks");
    const card = done.getByText("Release browser workflow", { exact: true });
    await expect(card).toBeVisible();
    await expect(done.getByRole("button", { name: "Move forward" })).toHaveCount(0);

    await card.locator("..").getByRole("button", { name: "Delete" }).click();
    await expect(done.getByText("Release browser workflow", { exact: true })).toHaveCount(0);
  } finally {
    await removeProject(request, name);
  }
});

test("filters tasks by priority and restores the complete task list", async ({
  page,
  request,
}) => {
  const name = projectName("filters");
  try {
    await page.goto("/");
    await createProjectFromUI(page, name);

    await page.getByRole("button", { name: "New task" }).click();
    await page.getByLabel("Task title").fill("High priority task");
    await page.getByLabel("Priority").selectOption("high");
    await page.getByRole("button", { name: "Save task" }).click();

    await page.getByRole("button", { name: "New task" }).click();
    await page.getByLabel("Task title").fill("Low priority task");
    await page.getByLabel("Priority").selectOption("low");
    await page.getByRole("button", { name: "Save task" }).click();

    await expect(page.getByText("High priority task", { exact: true })).toBeVisible();
    await expect(page.getByText("Low priority task", { exact: true })).toBeVisible();

    await page.getByLabel("Priority").selectOption("high");
    await expect(page.getByText("High priority task", { exact: true })).toBeVisible();
    await expect(page.getByText("Low priority task", { exact: true })).toHaveCount(0);

    await page.getByLabel("Priority").selectOption("");
    await expect(page.getByText("High priority task", { exact: true })).toBeVisible();
    await expect(page.getByText("Low priority task", { exact: true })).toBeVisible();
  } finally {
    await removeProject(request, name);
  }
});