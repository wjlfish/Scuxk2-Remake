let course_name = arguments[0];

let iframe = document.getElementById('ifra');
if (!iframe) {
    console.error("Iframe not found: ifra");
    return "no";
}

let iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
if (!iframeDoc) {
    console.error("Unable to access iframe document.");
    return "no";
}

let table_body = iframeDoc.getElementById('xirxkxkbody');
if (!table_body) {
    console.error("Table body not found in iframe: xirxkxkbody");
    return "no";
}

let rows = table_body.getElementsByTagName('tr');
console.log(`Found ${rows.length} rows in the table body.`);

for (var i = 0; i < rows.length; i++) {
    let row = rows[i];
    let cells = row.getElementsByTagName('td');
    console.log(`Row ${i + 1}: Found ${cells.length} cells.`);

    if (cells.length < 4) {
        console.warn(`Row ${i + 1} skipped: Less than 4 cells.`);
        continue;
    }

    let column_content = cells[2].innerHTML.trim();
    console.log(`Row ${i + 1}, Column 3 content: "${column_content}"`);

    if (column_content.indexOf(course_name) != -1) {
        console.log(`Match found in row ${i + 1}. Clicking the first column.`);
        let clickableElement = cells[0].getElementsByTagName('input')[0];
        if (clickableElement) {
            clickableElement.click();
            console.log("Click action performed.");
            return "yes";
        } else {
            console.error(`No clickable element found in Row ${i + 1}, Column 1.`);
            return "no";
        }
    }
}

console.log("No matching course found.");
return "no";
