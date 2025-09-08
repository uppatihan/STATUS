// Reload Page
console.log("| # H E L L O !");
const PATH = "http://localhost:8001/";
// console.log("API Path:", PATH);

window.addEventListener("DOMContentLoaded", () => {
    // วันนี้
    const day = new Date();
    // วันย้อนหลัง 
    const b7d = new Date(day);
    const b8d = new Date(day);

    b7d.setDate(day.getDate() - 7);
    b8d.setDate(day.getDate() - 8);

    document.getElementById("startDate").value = b8d.toISOString().split("T")[0];
    document.getElementById("endDate").value = b7d.toISOString().split("T")[0];
});


function getDate() {
    const startDate = document.forms["formDate"]["startDate"].value;
    const endDate = document.forms["formDate"]["endDate"].value;

    if (!startDate || !endDate) {
        console.log("ยังไม่ได้กรอกวันที่");
        alert("กรุณากรอกวันที่ให้ครบ");
        return;
    }

    fetchDate(startDate, endDate)
}

async function fetchDate(startDate, endDate) {
    const API = PATH + "main";
    const spinner = document.getElementById("spinner");

    try {
        spinner.classList.remove("hidden");

        const response = await fetch(API, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ startDate: startDate, endDate: endDate })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || response.statusText);
        }

        const data = await response.json();
        // console.log("Success:", data);
        postDate(data.data)

    } catch (err) {
        alert("เกิดข้อผิดพลาด : " + err)
    } finally {
        spinner.classList.add("hidden");
    }
}

let currentPage = 1;
const rowsPerPage = 50;
let allRows = []; // เก็บข้อมูลทั้งหมด

function postDate(data) {
    const thead = document.getElementById("tableHead");
    const tbody = document.getElementById("tableBody");
    const page = document.getElementById("page");
    const dateFilter = document.getElementById("dateFilter");

    // ล้างตารางเก่า
    thead.innerHTML = "";
    tbody.innerHTML = "";

    // เติม option ของวันที่
    dateFilter.innerHTML = `<option value="all">ทั้งหมด</option>`;
    for (const date in data) {
        const option = document.createElement("option");
        option.value = date;
        option.textContent = date;
        dateFilter.appendChild(option);
    }

    // รวมข้อมูล
    allRows = [];
    for (const date in data) {
        data[date].forEach(row => {
            row._date = date;
            allRows.push(row);
        });
    }

    if (allRows.length === 0) return;

    // สร้าง header
    const headers = Object.keys(allRows[0]);
    const trHead = document.createElement("tr");
    headers.forEach(header => {
        const th = document.createElement("th");
        th.textContent = header;
        th.className = "border px-4 py-2 bg-gray-800 text-white";
        trHead.appendChild(th);
    });
    thead.appendChild(trHead);

    page.classList.remove("hidden");

    // ✅ แสดงหน้าที่ 1 พร้อม pagination เลย
    currentPage = 1;
    showPage(currentPage, rowsPerPage, headers);
    const totalPages = Math.ceil(allRows.length / rowsPerPage);
    renderPagination(totalPages);

    // ✅ Event เมื่อเปลี่ยน dropdown
    dateFilter.addEventListener("change", () => {
        const selected = dateFilter.value;
        allRows = [];

        if (selected === "all") {
            for (const d in data) {
                data[d].forEach(row => {
                    row._date = d;
                    allRows.push(row);
                });
            }
        } else {
            data[selected].forEach(row => {
                row._date = selected;
                allRows.push(row);
            });
        }

        currentPage = 1;
        showPage(currentPage, rowsPerPage, headers);
        renderPagination(Math.ceil(allRows.length / rowsPerPage));
    });
}

function showPage(page, perPage, headers) {
    const tbody = document.getElementById("tableBody");
    tbody.innerHTML = "";

    const start = (page - 1) * perPage;
    const end = start + perPage;
    const displayRows = allRows.slice(start, end);

    displayRows.forEach((row, index) => {
        const tr = document.createElement("tr");
        tr.className = index % 2 === 0 ? "bg-gray-100 hover:bg-gray-200" : "bg-white hover:bg-gray-200";
        headers.forEach(header => {
            const td = document.createElement("td");
            td.textContent = row[header];
            td.className = "border px-4 py-2";
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    // อัปเดต info
    const pageInfo = document.getElementById("pageInfo");
    const totalRows = allRows.length;
    const showingStart = totalRows === 0 ? 0 : start + 1;
    const showingEnd = Math.min(end, totalRows);

    pageInfo.textContent = `รายการที่ ${showingStart}–${showingEnd} จาก ${totalRows} รายการ`;
}

// ปุ่ม Next / Prev
document.getElementById("prevPage").addEventListener("click", () => {
    if (currentPage > 1) {
        currentPage--;
        showPage(currentPage, rowsPerPage, Object.keys(allRows[0]));
        const totalPages = Math.ceil(allRows.length / rowsPerPage);
        renderPagination(totalPages);
    }
});
document.getElementById("nextPage").addEventListener("click", () => {
    const totalPages = Math.ceil(allRows.length / rowsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        showPage(currentPage, rowsPerPage, Object.keys(allRows[0]));
        const totalPages = Math.ceil(allRows.length / rowsPerPage);
        renderPagination(totalPages);

    }
});

function renderPagination(totalPages) {
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    let maxButtons = 5; // จำนวนปุ่มสูงสุดที่แสดง
    let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
    let endPage = startPage + maxButtons - 1;

    if (endPage > totalPages) {
        endPage = totalPages;
        startPage = Math.max(1, endPage - maxButtons + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        const btn = document.createElement("button");
        btn.textContent = i;
        btn.className = `px-3 py-1 rounded ${i === currentPage ? "bg-blue-600 text-white" : "bg-gray-300"}`;

        btn.addEventListener("click", () => {
            currentPage = i;
            showPage(currentPage, rowsPerPage, Object.keys(allRows[0]));
            renderPagination(totalPages);
        });

        pagination.appendChild(btn);
    }
}

document.getElementById("download").addEventListener("click", async () => {
    const DOWNLOAD = PATH + "download";

    const spinner = document.getElementById("spinner");
    spinner.classList.remove("hidden");

    try {
        const response = await fetch(DOWNLOAD, { method: "GET" });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || response.statusText);
        }

        alert("✅ ดาวน์โหลดไฟล์เสร็จเรียบร้อย");

    } catch (err) {
        alert("เกิดข้อผิดพลาด : " + err);
    } finally {
        spinner.classList.add("hidden");
    }
});
