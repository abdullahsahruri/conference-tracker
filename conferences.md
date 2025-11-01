---
layout: page
title: Conference Deadlines
subtitle: Automatically updated conference submission deadlines
---

<style>
    .conference-table {
        width: 100%;
        margin: 20px 0;
        border-collapse: collapse;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .conference-table th {
        background-color: #2c5aa0;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: 600;
    }
    .conference-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #ddd;
    }
    .conference-table tr:hover {
        background-color: #f5f5f5;
    }
    .conference-table tr:nth-child(even) {
        background-color: #fafafa;
    }
    .deadline {
        color: #d32f2f;
        font-weight: 600;
    }
    .conf-name {
        font-weight: 600;
        color: #333;
    }
    .conf-url {
        color: #1a73e8;
        text-decoration: none;
    }
    .conf-url:hover {
        text-decoration: underline;
    }
    .last-updated {
        text-align: right;
        color: #666;
        font-size: 0.9em;
        margin-top: 20px;
        font-style: italic;
    }
    .search-box {
        margin: 20px 0;
        padding: 10px;
        width: 100%;
        max-width: 400px;
        border: 2px solid #ddd;
        border-radius: 4px;
        font-size: 16px;
    }
    .filter-buttons {
        margin: 15px 0;
    }
    .filter-btn {
        padding: 8px 16px;
        margin: 5px;
        border: none;
        border-radius: 4px;
        background-color: #e0e0e0;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .filter-btn:hover {
        background-color: #d0d0d0;
    }
    .filter-btn.active {
        background-color: #2c5aa0;
        color: white;
    }
</style>

<div class="conference-tracker">
    <p style="font-size: 1.1em; margin-bottom: 20px;">
        🔄 Automatically updated daily at 9:00 AM UTC |
        📧 Email notifications for deadline changes |
        🗓️ Synced with Google Calendar
    </p>

    <input type="text" id="searchBox" class="search-box" placeholder="🔍 Search conferences...">

    <div class="filter-buttons">
        <button class="filter-btn active" onclick="filterTable('all')">All</button>
        <button class="filter-btn" onclick="filterTable('2025')">2025</button>
        <button class="filter-btn" onclick="filterTable('2026')">2026</button>
        <button class="filter-btn" onclick="filterTable('upcoming')">Upcoming Deadlines</button>
    </div>

    <div id="tableContainer">
        <!-- Table will be loaded here -->
        <p style="text-align: center; padding: 40px;">
            <em>Loading conference data...</em>
        </p>
    </div>

    <p class="last-updated" id="lastUpdated">Last updated: Loading...</p>
</div>

<script>
// Load conference data from JSON
async function loadConferences() {
    try {
        const response = await fetch('https://raw.githubusercontent.com/abdullahsahruri/conference-tracker/main/conference_database.json');
        const data = await response.json();

        displayConferences(data);
        setupSearch(data);
    } catch (error) {
        document.getElementById('tableContainer').innerHTML =
            '<p style="color: red;">Error loading conference data. Please check back later.</p>';
        console.error('Error:', error);
    }
}

function displayConferences(data) {
    const conferences = Object.values(data);

    // Sort by deadline
    conferences.sort((a, b) => {
        const dateA = new Date(a.paper_deadline || '9999-12-31');
        const dateB = new Date(b.paper_deadline || '9999-12-31');
        return dateA - dateB;
    });

    let html = `
        <table class="conference-table" id="confTable">
            <thead>
                <tr>
                    <th>Conference</th>
                    <th>Paper Deadline</th>
                    <th>Website</th>
                    <th>Last Checked</th>
                </tr>
            </thead>
            <tbody>
    `;

    conferences.forEach(conf => {
        const deadline = conf.paper_deadline || 'TBD';
        const lastChecked = conf.last_checked ? conf.last_checked.split('T')[0] : 'N/A';
        const url = conf.url || '#';
        const urlDisplay = url.length > 50 ? url.substring(0, 50) + '...' : url;

        html += `
            <tr data-conference="${conf.name.toLowerCase()}" data-deadline="${deadline}">
                <td class="conf-name">${conf.name}</td>
                <td class="deadline">${deadline}</td>
                <td><a href="${url}" target="_blank" class="conf-url">${urlDisplay}</a></td>
                <td>${lastChecked}</td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    document.getElementById('tableContainer').innerHTML = html;
    document.getElementById('lastUpdated').textContent =
        `Last updated: ${new Date().toLocaleDateString()} | Total conferences: ${conferences.length}`;
}

function setupSearch(data) {
    const searchBox = document.getElementById('searchBox');
    searchBox.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = document.querySelectorAll('#confTable tbody tr');

        rows.forEach(row => {
            const confName = row.dataset.conference;
            if (confName.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

function filterTable(filter) {
    const rows = document.querySelectorAll('#confTable tbody tr');
    const buttons = document.querySelectorAll('.filter-btn');

    // Update active button
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    const now = new Date();

    rows.forEach(row => {
        const confName = row.dataset.conference;
        const deadline = row.dataset.deadline;
        const deadlineDate = new Date(deadline);

        let show = false;

        switch(filter) {
            case 'all':
                show = true;
                break;
            case '2025':
                show = confName.includes('2025');
                break;
            case '2026':
                show = confName.includes('2026');
                break;
            case 'upcoming':
                show = deadlineDate > now;
                break;
        }

        row.style.display = show ? '' : 'none';
    });
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', loadConferences);
</script>

---

## About This Tracker

This conference deadline tracker is powered by an **intelligent automated system** that:

- 🔍 **Automatically discovers** conferences by searching the web
- 🧠 **Extracts deadlines** from any conference website using smart parsing
- 🔄 **Detects changes** daily and sends email notifications
- 📊 **Maintains a database** with historical change tracking
- 🗓️ **Syncs to Google Calendar** automatically
- 🤖 **Runs daily** via GitHub Actions at 9 AM UTC

### Features:
- ✅ Real-time deadline tracking
- ✅ Handles changing conference URLs year-to-year
- ✅ Email alerts for deadline changes
- ✅ Search and filter functionality
- ✅ Mobile-responsive design

### Source Code:
[GitHub Repository](https://github.com/abdullahsahruri/conference-tracker)

---

*Last auto-update: Check the table above*
