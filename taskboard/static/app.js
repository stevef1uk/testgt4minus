(() => {
  "use strict";

  const state = { projects: [], projectId: null, tasks: [] };
  const byId = (id) => document.getElementById(id);

  function showError(message) {
    const area = byId("error-message");
    if (!area) return;
    area.textContent = message || "";
    area.hidden = !message;
  }

  async function api(path, options = {}) {
    const response = await fetch(path, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    });
    if (!response.ok) {
      let message = `Request failed (${response.status})`;
      try {
        const body = await response.json();
        message = body.error || body.detail || message;
      } catch (_) {}
      throw new Error(message);
    }
    return response.status === 204 ? null : response.json();
  }

  function renderProjects() {
    const select = byId("project-select");
    const empty = byId("projects-empty");
    const deleteButton = byId("delete-project");
    select.textContent = "";

    if (!state.projects.length) {
      select.append(new Option("No projects", ""));
      state.projectId = null;
      empty.hidden = false;
      deleteButton.disabled = true;
      byId("task-panel").hidden = true;
      renderTasks();
      return;
    }

    empty.hidden = true;
    if (!state.projects.some((project) => project.id === state.projectId)) {
      state.projectId = state.projects[0].id;
    }
    state.projects.forEach((project) => {
      select.append(new Option(project.name, String(project.id)));
    });
    select.value = String(state.projectId);
    deleteButton.disabled = false;
    byId("task-panel").hidden = false;
  }

  function renderTasks() {
    ["todo", "doing", "done"].forEach((status) => {
      byId(`${status}-list`).textContent = "";
    });

    const empty = byId("tasks-empty");
    if (!state.projectId || !state.tasks.length) {
      empty.hidden = false;
      return;
    }
    empty.hidden = true;

    state.tasks.forEach((task) => {
      const status = task.status === "in_progress" ? "doing" : task.status;
      const card = document.createElement("article");
      card.className = "task-card";
      card.dataset.taskId = String(task.id);

      const title = document.createElement("h4");
      title.textContent = task.title;
      card.append(title);

      const priority = document.createElement("span");
      priority.className = "task-priority";
      priority.textContent = task.priority;
      card.append(priority);

      if (task.description) {
        const description = document.createElement("p");
        description.textContent = task.description;
        card.append(description);
      }

      const actions = document.createElement("div");
      actions.className = "task-actions";
      if (status !== "done") {
        const move = document.createElement("button");
        move.type = "button";
        move.textContent = "Move forward";
        move.dataset.action = "move";
        actions.append(move);
      }

      for (const [action, label] of [["edit", "Edit"], ["delete", "Delete"]]) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = label;
        button.dataset.action = action;
        if (action === "delete") button.className = "danger";
        actions.append(button);
      }
      card.append(actions);
      byId(`${status}-list`).append(card);
    });
  }

  async function loadProjects() {
    state.projects = await api("/api/projects");
    renderProjects();
    await loadTasks();
  }

  async function loadTasks() {
    if (!state.projectId) {
      state.tasks = [];
      renderTasks();
      return;
    }
    const query = new URLSearchParams();
    const status = byId("status-filter").value;
    const priority = byId("priority-filter").value;
    if (status !== "all") query.set("status", status);
    if (priority !== "all") query.set("priority", priority);
    const suffix = query.toString() ? `?${query}` : "";
    state.tasks = await api(`/api/projects/${state.projectId}/tasks${suffix}`);
    renderTasks();
  }

  byId("project-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const project = await api("/api/projects", {
        method: "POST",
        body: JSON.stringify({ name: byId("project-name").value }),
      });
      byId("project-name").value = "";
      state.projectId = project.id;
      showError("");
      await loadProjects();
    } catch (error) {
      showError(error.message);
    }
  });

  byId("project-select").addEventListener("change", async (event) => {
    state.projectId = Number(event.target.value) || null;
    try {
      showError("");
      await loadTasks();
    } catch (error) {
      showError(error.message);
    }
  });

  byId("task-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!state.projectId) return;
    try {
      await api(`/api/projects/${state.projectId}/tasks`, {
        method: "POST",
        body: JSON.stringify({
          title: byId("task-title").value,
          description: byId("task-description").value,
          priority: byId("task-priority").value,
        }),
      });
      event.target.reset();
      showError("");
      await loadTasks();
    } catch (error) {
      showError(error.message);
    }
  });

  ["status-filter", "priority-filter"].forEach((id) => {
    byId(id).addEventListener("change", () =>
      loadTasks().catch((error) => showError(error.message))
    );
  });

  byId("delete-project").addEventListener("click", async () => {
    const project = state.projects.find((item) => item.id === state.projectId);
    if (!project || !window.confirm(`Delete project "${project.name}"?`)) return;
    try {
      await api(`/api/projects/${project.id}`, { method: "DELETE" });
      state.projectId = null;
      await loadProjects();
    } catch (error) {
      showError(error.message);
    }
  });

  byId("task-panel").addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    const card = button && button.closest(".task-card");
    if (!button || !card) return;

    const task = state.tasks.find(
      (item) => item.id === Number(card.dataset.taskId)
    );
    if (!task) return;

    try {
      if (button.dataset.action === "delete") {
        await api(`/api/tasks/${task.id}`, { method: "DELETE" });
      } else if (button.dataset.action === "move") {
        const next = { todo: "doing", in_progress: "done", doing: "done" }[
          task.status
        ];
        await api(`/api/tasks/${task.id}`, {
          method: "PATCH",
          body: JSON.stringify({ status: next }),
        });
      } else if (button.dataset.action === "edit") {
        const title = window.prompt("Task title", task.title);
        if (title === null) return;
        const description = window.prompt(
          "Description",
          task.description || ""
        );
        if (description === null) return;
        await api(`/api/tasks/${task.id}`, {
          method: "PATCH",
          body: JSON.stringify({
            title,
            description,
            priority: task.priority,
          }),
        });
      }
      await loadTasks();
    } catch (error) {
      showError(error.message);
    }
  });

  loadProjects().catch((error) => showError(error.message));
})();