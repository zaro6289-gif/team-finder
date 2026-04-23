(function(){
  document.addEventListener("DOMContentLoaded", () => {
    const skillsList = document.getElementById("skills-list");
    if (!skillsList) return;

    const userId = document.body.dataset.userId || (window.location.pathname.match(/\/users\/(\d+)/) || [])[1];
    const showAddBtn = document.getElementById("show-add-skill-btn");
    const addForm = document.getElementById("add-skill-form");
    const addBtn = document.getElementById("add-skill-btn");
    const cancelBtn = document.getElementById("cancel-skill-btn");
    const skillInput = document.getElementById("skill-input");
    const suggestions = document.getElementById("skill-suggestions");

    if (!showAddBtn || !addForm) return;

    showAddBtn.addEventListener("click", () => {
      addForm.style.display = "flex";
      showAddBtn.style.display = "none";
      skillInput.focus();
    });

    if (cancelBtn) {
      cancelBtn.addEventListener("click", () => {
        addForm.style.display = "none";
        showAddBtn.style.display = "inline-block";
        skillInput.value = "";
        suggestions.innerHTML = "";
        suggestions.style.display = "none";
      });
    }

    let t = null;
    skillInput.addEventListener("input", () => {
      const q = skillInput.value.trim();
      clearTimeout(t);
      if (!q) {
        suggestions.style.display = "none";
        suggestions.innerHTML = "";
        return;
      }
      t = setTimeout(async () => {
        const res = await fetch(`/users/skills/autocomplete/?q=${encodeURIComponent(q)}`);
        if (!res.ok) return;
        const data = await res.json();

        suggestions.innerHTML = "";
        data.forEach(s => {
          const li = document.createElement("li");
          li.textContent = s.name;
          li.dataset.id = s.id;
          li.className = "suggestion-item";
          suggestions.appendChild(li);
        });

        const exact = data.some(s => s.name.toLowerCase() === q.toLowerCase());
        if (!exact) {
          const liNew = document.createElement("li");
          liNew.textContent = `Создать "${q}"`;
          liNew.dataset.name = q;
          liNew.className = "create-new";
          suggestions.appendChild(liNew);
        }

        suggestions.style.display = "block";
      }, 200);
    });

    suggestions.addEventListener("mousedown", async (e) => {
      const li = e.target.closest("li");
      if (!li) return;

      if (li.classList.contains("create-new")) {
        await addSkillByName(li.dataset.name);
      } else if (li.dataset.id) {
        await addSkillById(li.dataset.id);
      }
      hideInput();
    });

    skillInput.addEventListener("keydown", async (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const q = skillInput.value.trim();
        if (!q) return;

        const first = suggestions.querySelector("li");
        if (first && first.dataset.id) {
          await addSkillById(first.dataset.id);
        } else {
          await addSkillByName(q);
        }
        hideInput();
      }
      if (e.key === "Escape") {
        hideInput();
      }
    });

    skillInput.addEventListener("blur", () => setTimeout(hideInput, 120));

    function hideInput() {
      addForm.style.display = "none";
      suggestions.style.display = "none";
      showAddBtn.style.display = "inline-block";
    }

    async function addSkillById(skillId) {
      const formData = new FormData();
      formData.append('skill_id', skillId);
      
      const res = await fetch(`/users/${userId}/skills/add/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        body: formData
      });
      if (res.ok) {
        location.reload();
      }
    }

    async function addSkillByName(name) {
      const formData = new FormData();
      formData.append('name', name);
      
      const res = await fetch(`/users/${userId}/skills/add/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        body: formData
      });
      if (res.ok) {
        location.reload();
      }
    }

    skillsList.addEventListener("click", async (e) => {
      const btn = e.target.closest(".remove-skill-btn");
      if (!btn) return;
      
      const skillId = btn.dataset.skillId;
      if (confirm('Удалить навык?')) {
        const res = await fetch(`/users/${userId}/skills/${skillId}/remove/`, {
          method: "POST",
          headers: { "X-CSRFToken": getCookie("csrftoken") }
        });
        if (res.ok) {
          location.reload();
        }
      }
    });

    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
          cookie = cookie.trim();
          if (cookie.startsWith(name + "=")) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  });
})();
function applySkillFilter() {
    const skillSelect = document.getElementById('skill-filter');
    if (skillSelect) {
        const skill = skillSelect.value;
        const url = new URL(window.location.href);
        if (skill) {
            url.searchParams.set('skill', skill);
        } else {
            url.searchParams.delete('skill');
        }
        window.location.href = url.toString();
    }
}