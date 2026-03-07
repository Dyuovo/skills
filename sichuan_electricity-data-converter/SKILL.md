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

// 获取命令行参数 (例如: node script.js --interval=15)
const args = process.argv.slice(2);
const intervalArg = args.find(arg => arg.startsWith('--interval='));
// 默认间隔为 60 分钟 (1小时)
const interval = intervalArg ? intervalArg.split('=')[1] : '60'; 
const is15Min = interval === '15';

// 基础配置
const PRICE_KEYWORD = '电价';
const QUANTITY_KEYWORD = '电量';

console.log(`\n⚙️  运行模式: ${is15Min ? '15分钟间隔 (96点输出)' : '1小时聚合 (24点输出)'}\n`);

// 生成时间标签工具函数
function generateTimeLabels(is15Min) {
    const labels = [];
    if (is15Min) {
        for (let h = 0; h < 24; h++) {
            for (let m = 0; m < 60; m += 15) {
                labels.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`);
            }
        }
    } else {
        for (let h = 0; h < 24; h++) {
            labels.push(`${String(h).padStart(2, '0')}:00`);
        }
    }
    return labels;
}

function processFile(filename) {
    console.log(`Processing: ${filename}`);
    const workbook = XLSX.readFile(filename);
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

    const isPrice = filename.includes(PRICE_KEYWORD);
    const isQuantity = filename.includes(QUANTITY_KEYWORD);
    
    // 判断聚合方式（如果是15分钟模式，此设置将不被触发）
    const useSum = isQuantity;
    if (!is15Min) {
        console.log(`Type: ${isPrice ? 'Price' : (isQuantity ? 'Quantity' : 'Unknown')}, Aggregation: ${useSum ? 'Sum' : 'Average'}`);
    }

    const processedData = [];
    let dataRows = [];
    
    // 提取包含数据的6行
    for (let i = 0; i < data.length; i++) {
        const row = data[i];
        const hasTimeRange = row.some(cell => typeof cell === 'string' && /\d{2}:\d{2}-\d{2}:\d{2}/.test(cell));
        if (hasTimeRange) {
            dataRows.push(row);
        }
    }

    if (dataRows.length !== 6) {
        console.warn(`Warning: Expected 6 rows of data, found ${dataRows.length} in ${filename}. Skipping.`);
        return;
    }

    // 处理数据行
    dataRows.forEach((row, rowIndex) => {
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

        // 取出当前4小时块内的16个数据点
        const values = row.slice(valueStartIndex, valueStartIndex + 16);
        const numericValues = values.map(v => {
            const num = parseFloat(v);
            return isNaN(num) ? 0 : num; // 处理空值或非数字字符
        });
        
        if (is15Min) {
            // 【15分钟模式】：直接推入16个原始数据
            processedData.push(...numericValues);
        } else {
            // 【1小时模式】：将16个数据分成4块，每块4个数据进行聚合
            for (let h = 0; h < 4; h++) {
                const chunk = numericValues.slice(h * 4, (h + 1) * 4);
                let result = 0;
                
                if (chunk.length > 0) {
                    const sum = chunk.reduce((a, b) => a + b, 0);
                    result = useSum ? sum : sum / chunk.length;
                }
                processedData.push(result);
            }
        }
    });

    // 创建新的Excel工作簿
    const timeLabels = generateTimeLabels(is15Min);
    const newWb = XLSX.utils.book_new();
    const newWsData = [
        ["Time", "Value"]
    ];
    
    processedData.forEach((val, index) => {
        // 防止数据点越界导致没有时间标签
        const label = timeLabels[index] || `Point_${index + 1}`;
        newWsData.push([label, val]);
    });

    const sheetTitle = is15Min ? "96Points" : "24Points";
    const newWs = XLSX.utils.aoa_to_sheet(newWsData);
    XLSX.utils.book_append_sheet(newWb, newWs, sheetTitle);
    
    // 动态生成文件名后缀
    const suffix = is15Min ? "_96点(15min).xlsx" : "_24点(1h).xlsx";
    const newFilename = path.parse(filename).name + suffix;
    
    XLSX.writeFile(newWb, newFilename);
    console.log(`Saved: ${newFilename}\n`);
}

// 扫描当前目录下的文件并排除已生成的文件
const allFiles = fs.readdirSync('.').filter(f => 
    f.endsWith('.xlsx') && 
    !f.endsWith('_24点(1h).xlsx') && 
    !f.endsWith('_96点(15min).xlsx') && 
    !f.startsWith('~$')
);

if (allFiles.length === 0) {
    console.log("No valid Excel files to process found in the current directory.");
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

