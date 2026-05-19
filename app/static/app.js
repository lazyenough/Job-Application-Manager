const previewBtn = document.getElementById("previewBtn");
const ingestBtn = document.getElementById("ingestBtn");
const jobUrlInput = document.getElementById("jobUrl");

const errorBox = document.getElementById("errorBox");
const successBox = document.getElementById("successBox");
const resultCard = document.getElementById("resultCard");

const jobTitle = document.getElementById("jobTitle");
const companyName = document.getElementById("companyName");
const workLocation = document.getElementById("workLocation");
const workMode = document.getElementById("workMode");
const jobSummary = document.getElementById("jobSummary");
const jobDescriptionPreview = document.getElementById("jobDescriptionPreview");

const loadJobsBtn = document.getElementById("loadJobsBtn");
const savedJobsCard = document.getElementById("savedJobsCard");
const savedJobsList = document.getElementById("savedJobsList");

function setValue(element, value) {
    element.textContent = value ?? "Not available";
}

function resetMessages() {
    errorBox.style.display = "none";
    successBox.style.display = "none";
    resultCard.style.display = "none";
}

function renderSavedJobs(jobs) {
    if (!jobs.length) {
        savedJobsList.innerHTML = "<p>No saved jobs found.</p>";
        savedJobsCard.style.display = "block";
        return;
    }

    savedJobsList.innerHTML = jobs.map(job => `
        <div class="job-item">
            <h3>${job.job_title ?? "Untitled Job"}</h3>
            <div class="job-meta">
                <strong>Company:</strong> ${job.company_name ?? "Not available"} |
                <strong>Location:</strong> ${job.location ?? "Not available"} |
                <strong>Work Mode:</strong> ${job.work_mode ?? "Not available"} |
                <strong>Status:</strong> ${job.status ?? "Not available"}
            </div>
            <p><strong>Summary:</strong> ${job.job_summary ?? "Not available"}</p>
            <div class="status-update-row">
                <select id="status-${job.id}">
                    <option value="saved" ${job.status === "saved" ? "selected" : ""}>saved</option>
                    <option value="to_apply" ${job.status === "to_apply" ? "selected" : ""}>to_apply</option>
                    <option value="applied" ${job.status === "applied" ? "selected" : ""}>applied</option>
                    <option value="interview" ${job.status === "interview" ? "selected" : ""}>interview</option>
                    <option value="offer" ${job.status === "offer" ? "selected" : ""}>offer</option>
                    <option value="rejected" ${job.status === "rejected" ? "selected" : ""}>rejected</option>
                    <option value="archived" ${job.status === "archived" ? "selected" : ""}>archived</option>
                </select>
                <button onclick="updateJobStatus('${job.id}')">Update Status</button>
                <button class="delete-btn" onclick="deleteJob('${job.id}')">Delete Job</button>
            </div>
        </div>
    `).join("");

    savedJobsCard.style.display = "block";
}

async function updateJobStatus(jobId) {
    const statusSelect = document.getElementById(`status-${jobId}`);
    const newStatus = statusSelect.value;

    errorBox.style.display = "none";
    successBox.style.display = "none";

    try {
        const response = await fetch(`/jobs/${jobId}`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ status: newStatus })
        });

        let data;
        try {
            data = await response.json();
        } catch (error) {
            errorBox.textContent = "API did not return valid JSON.";
            errorBox.style.display = "block";
            return;
        }

        if (!response.ok) {
            errorBox.textContent = data.detail || "Something went wrong while updating job status.";
            errorBox.style.display = "block";
            return;
        }

        successBox.innerHTML = `
            <strong>Status updated successfully.</strong><br>
            Job ID: ${data.id}<br>
            New Status: ${data.status}
        `;
        successBox.style.display = "block";

        const refreshedJobs = await fetch("/jobs");
        const refreshedData = await refreshedJobs.json();
        renderSavedJobs(refreshedData);
    } catch (error) {
        errorBox.textContent = "Something went wrong while updating the job status.";
        errorBox.style.display = "block";
    }
}

async function deleteJob(jobId) {
    const confirmDelete = confirm("Are you sure you want to delete this job?");

    if (!confirmDelete) {
        return;
    }

    errorBox.style.display = "none";
    successBox.style.display = "none";

    try {
        const response = await fetch(`/jobs/${jobId}`, {
            method: "DELETE"
        });

        let data;
        try {
            data = await response.json();
        } catch (error) {
            errorBox.textContent = "API did not return valid JSON.";
            errorBox.style.display = "block";
            return;
        }

        if (!response.ok) {
            errorBox.textContent = data.detail || "Something went wrong while deleting the job.";
            errorBox.style.display = "block";
            return;
        }

        successBox.innerHTML = `
            <strong>Job deleted successfully.</strong><br>
            ${data.message}
        `;
        successBox.style.display = "block";

        const refreshedJobs = await fetch("/jobs");
        const refreshedData = await refreshedJobs.json();
        renderSavedJobs(refreshedData);
    } catch (error) {
        errorBox.textContent = "Something went wrong while deleting the job.";
        errorBox.style.display = "block";
    }
}

previewBtn.addEventListener("click", async () => {
    const jobUrl = jobUrlInput.value.trim();

    resetMessages();

    if (!jobUrl) {
        errorBox.textContent = "Please enter a job URL.";
        errorBox.style.display = "block";
        return;
    }

    previewBtn.disabled = true;
    previewBtn.textContent = "Loading...";

    try {
        const response = await fetch("/jobs/ingest/preview", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ job_url: jobUrl })
        });

        let data;
        try {
            data = await response.json();
        } catch (error) {
            errorBox.textContent = "API did not return valid JSON.";
            errorBox.style.display = "block";
            return;
        }

        if (!response.ok) {
            errorBox.textContent = data.detail || "Something went wrong.";
            errorBox.style.display = "block";
            return;
        }

        setValue(jobTitle, data.job_title);
        setValue(companyName, data.company_name);
        setValue(workLocation, data.location);
        setValue(workMode, data.work_mode);
        setValue(jobSummary, data.job_summary);
        setValue(jobDescriptionPreview, data.job_description_preview);

        resultCard.style.display = "block";
    } catch (error) {
        errorBox.textContent = "Something went wrong while calling the API.";
        errorBox.style.display = "block";
    } finally {
        previewBtn.disabled = false;
        previewBtn.textContent = "Preview Extraction";
    }
});

ingestBtn.addEventListener("click", async () => {
    const jobUrl = jobUrlInput.value.trim();

    errorBox.style.display = "none";
    successBox.style.display = "none";

    if (!jobUrl) {
        errorBox.textContent = "Please enter a job URL.";
        errorBox.style.display = "block";
        return;
    }

    ingestBtn.disabled = true;
    ingestBtn.textContent = "Saving...";

    try {
        const response = await fetch("/jobs/ingest", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ job_url: jobUrl })
        });

        let data;
        try {
            data = await response.json();
        } catch (error) {
            errorBox.textContent = "API did not return valid JSON.";
            errorBox.style.display = "block";
            return;
        }

        if (!response.ok) {
            errorBox.textContent = data.detail || "Something went wrong while saving the job.";
            errorBox.style.display = "block";
            return;
        }

        successBox.innerHTML = `
            <strong>Job saved successfully.</strong><br>
            Job ID: ${data.id}<br>
            Status: ${data.status}
        `;
        successBox.style.display = "block";
    } catch (error) {
        errorBox.textContent = "Something went wrong while calling the API.";
        errorBox.style.display = "block";
    } finally {
        ingestBtn.disabled = false;
        ingestBtn.textContent = "Ingest Job";
    }
});

loadJobsBtn.addEventListener("click", async () => {
    errorBox.style.display = "none";
    successBox.style.display = "none";

    loadJobsBtn.disabled = true;
    loadJobsBtn.textContent = "Loading...";

    try {
        const response = await fetch("/jobs");

        let data;
        try {
            data = await response.json();
        } catch (error) {
            errorBox.textContent = "API did not return valid JSON.";
            errorBox.style.display = "block";
            return;
        }

        if (!response.ok) {
            errorBox.textContent = data.detail || "Something went wrong while loading jobs.";
            errorBox.style.display = "block";
            return;
        }

        renderSavedJobs(data);
    } catch (error) {
        errorBox.textContent = "Something went wrong while loading saved jobs.";
        errorBox.style.display = "block";
    } finally {
        loadJobsBtn.disabled = false;
        loadJobsBtn.textContent = "Load Saved Jobs";
    }
});