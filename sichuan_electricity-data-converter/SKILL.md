---
name: "electricity-data-converter"
description: "Converts electricity market Excel files (Price/Quantity) from horizontal 15-min intervals to vertical 24-hour format. Invoke when processing electricity data files."
---

# Electricity Data Converter

This skill converts electricity market data files from a horizontal, 15-minute interval format (organized in 4-hour blocks) into a vertical, 24-hour format.

## Functionality
- Identifies Excel files containing "电价" (Price) or "电量" (Quantity).
- **Price Files**: Averages the four 15-minute data points for each hour.
- **Quantity Files**: Sums the four 15-minute data points for each hour.
- **Input Format**: Expects 6 rows of data, each representing a 4-hour block (e.g., 00:00-04:00, 04:00-08:00, etc.).
- **Output**: Generates a new file with the suffix `_24点.xlsx` containing two columns: `Hour` (0-23) and `Value`.

## Usage Instructions

1. Ensure the directory contains the target `.xlsx` files.
2. Ensure Node.js is installed and the `xlsx` package is available (`npm install xlsx`).
3. Create and run the following Node.js script to perform the conversion:

```javascript
const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

// Configuration
const PRICE_KEYWORD = '电价';
const QUANTITY_KEYWORD = '电量';

function processFile(filename) {
    console.log(`Processing: ${filename}`);
    const workbook = XLSX.readFile(filename);
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

    const isPrice = filename.includes(PRICE_KEYWORD);
    const isQuantity = filename.includes(QUANTITY_KEYWORD);
    
    // Determine aggregation method
    // Default to average if unknown, but for 'quantity' use sum
    const useSum = isQuantity;
    console.log(`Type: ${isPrice ? 'Price' : (isQuantity ? 'Quantity' : 'Unknown')}, Aggregation: ${useSum ? 'Sum' : 'Average'}`);

    const hourlyData = [];
    
    // Iterate through rows that contain data
    // The structure seems to be: Header, then 6 rows of data (each 4 hours)
    let dataRows = [];
    for (let i = 0; i < data.length; i++) {
        const row = data[i];
        // Check if row has time range like "00:15-04:00"
        const hasTimeRange = row.some(cell => typeof cell === 'string' && /\d{2}:\d{2}-\d{2}:\d{2}/.test(cell));
        if (hasTimeRange) {
            dataRows.push(row);
        }
    }

    if (dataRows.length !== 6) {
        console.warn(`Warning: Expected 6 rows of data, found ${dataRows.length} in ${filename}. Skipping.`);
        return;
    }

    // Process each of the 6 rows (each represents 4 hours)
    dataRows.forEach((row, rowIndex) => {
        // Find where the numbers start.
        let valueStartIndex = -1;
        for (let j = 0; j < row.length; j++) {
            if (typeof row[j] === 'string' && /\d{2}:\d{2}-\d{2}:\d{2}/.test(row[j])) {
                valueStartIndex = j + 1;
                break;
            }
        }

        if (valueStartIndex === -1) {
            console.error(`Could not find time range in row ${rowIndex}`);
            return;
        }

        const values = row.slice(valueStartIndex, valueStartIndex + 16);
        
        // Process 4 chunks of 4 values (16 values total)
        for (let h = 0; h < 4; h++) {
            const chunk = values.slice(h * 4, (h + 1) * 4);
            // Convert to numbers and filter valid
            const numericChunk = chunk.map(v => parseFloat(v)).filter(v => !isNaN(v));
            
            if (numericChunk.length === 0) {
                hourlyData.push(0);
                continue;
            }

            let result;
            if (useSum) {
                result = numericChunk.reduce((a, b) => a + b, 0);
            } else {
                // Average
                const sum = numericChunk.reduce((a, b) => a + b, 0);
                result = sum / numericChunk.length;
            }
            hourlyData.push(result);
        }
    });

    // Create new workbook
    const newWb = XLSX.utils.book_new();
    const newWsData = [
        ["Hour", "Value"]
    ];
    
    hourlyData.forEach((val, index) => {
        newWsData.push([index, val]); // 0-23
    });

    const newWs = XLSX.utils.aoa_to_sheet(newWsData);
    XLSX.utils.book_append_sheet(newWb, newWs, "24Points");
    
    const newFilename = path.parse(filename).name + "_24点.xlsx";
    XLSX.writeFile(newWb, newFilename);
    console.log(`Saved: ${newFilename}`);
}

const allFiles = fs.readdirSync('.').filter(f => f.endsWith('.xlsx') && !f.endsWith('_24点.xlsx') && !f.startsWith('~$'));

if (allFiles.length === 0) {
    console.log("No files to process found.");
} else {
    allFiles.forEach(file => {
        try {
            processFile(file);
        } catch (e) {
            console.error(`Error processing ${file}:`, e);
        }
    });
}
```
