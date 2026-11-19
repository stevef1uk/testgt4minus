(function () {
  "use strict";

  var projects = [];
  var formRegion = document.getElementById("project-form-region");
  var form = document.getElementById("project-form");
  var list = document.getElementById("project-list");
  var empty = document.getElementById("empty-state");
  var error = document.getElementById("error-state");
  var loading = document.getElementById("loading-state");
  var search = document.getElementById("project-filter");

  function showError(message) {
    error.textContent = message || "";
    error.hidden = !message;
  }

  function showForm() {
    form.reset();
    formRegion.hidden = false;
    document.getElementById("name").focus();
  }

  function hideForm() {
    formRegion.hidden = true;
    form.reset();
  }

  function visibleProjects() {
    var query = search.value.trim().toLowerCase();
    return projects.filter(function (project) {
      return !query || project.name.toLowerCase().indexOf(query) !== -1;
    });
  }

  function render() {
    list.replaceChildren();
    var visible = visibleProjects();
    empty.hidden = visible.length !== 0;
    visible.forEach(function (project) {
      var card = document.createElement("article");
      card.className = "project-card";
      card.dataset.id = project.id;

      var heading = document.createElement("h2");
      heading.textContent = project.name;
      card.appendChild(heading);

      var created = document.createElement("p");
      created.className = "project-meta";
      created.textContent = "Created " + project.created_at;
      card.appendChild(created);

      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "button button-secondary";
      remove.textContent = "Delete";
      remove.addEventListener("click", function () {
        deleteProject(project.id);
      });
      card.appendChild(remove);
      list.appendChild(card);
    });
  }

  function loadProjects() {
    loading.hidden = false;
    showError("");
    return fetch("/api/projects")
      .then(function (response) {
        if (!response.ok) throw new Error("Unable to load projects.");
        return response.json();
      })
      .then(function (data) {
        projects = data;
        render();
      })
      .catch(function (cause) {
        showError(cause.message);
      })
      .then(function () {
        loading.hidden = true;
      });
  }

  function deleteProject(id) {
    return fetch("/api/projects/" + encodeURIComponent(id), { method: "DELETE" })
      .then(function (response) {
        if (!response.ok) throw new Error("Unable to delete project.");
        return loadProjects();
      })
      .catch(function (cause) {
        showError(cause.message);
      });
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var name = document.getElementById("name").value.trim();
    if (!name) return;

    fetch("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name })
    })
      .then(function (response) {
        if (!response.ok) throw new Error("Unable to create project.");
        return response.json();
      })
      .then(function () {
        hideForm();
        return loadProjects();
      })
      .catch(function (cause) {
        showError(cause.message);
      });
  });

  document.getElementById("new-project").addEventListener("click", showForm);
  document.getElementById("cancel-project").addEventListener("click", hideForm);
  search.addEventListener("input", render);
  loadProjects();
}());