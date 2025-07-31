from flask import Flask, render_template_string, request, jsonify
import time
import json
import webbrowser
import threading
import os

app = Flask(__name__)

# Global variable to track if browser has been opened
browser_opened = False

# HTML template with embedded CSS and JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cannabinoid & Terpene Effects Guide</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #4CAF50, #2E7D32);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            margin: 0;
            font-size: 2.2em;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
        .input-section, .results-section, .guide-section, .mixes-section, .examples-section, .scheduler-section, .search-section, .dosage-section {
            flex: 1;
            min-width: 300px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .compound-group {
            margin-bottom: 25px;
        }
        h2 {
            color: #2E7D32;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        .compound-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 15px;
        }
        .compound-item {
            display: flex;
            flex-direction: column;
        }
        label {
            font-weight: bold;
            margin-bottom: 5px;
            color: #444;
        }
        input, select {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            width: 100%;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 20px;
            font-size: 18px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            font-weight: bold;
            transition: background 0.3s;
            margin: 5px 0;
        }
        button:hover {
            background: #45a049;
        }
        .btn-secondary {
            background: #2196F3;
        }
        .btn-secondary:hover {
            background: #1976D2;
        }
        .btn-danger {
            background: #f44336;
        }
        .btn-danger:hover {
            background: #d32f2f;
        }
        .btn-medical {
            background: #FF9800;
        }
        .btn-medical:hover {
            background: #F57C00;
        }
        .btn-recreational {
            background: #9C27B0;
        }
        .btn-recreational:hover {
            background: #7B1FA2;
        }
        .results-content, .guide-content, .mixes-content, .examples-content, .scheduler-content, .search-content, .dosage-content {
            min-height: 400px;
        }
        .effect-item {
            margin-bottom: 15px;
        }
        .effect-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .intensity-bar {
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
        }
        .intensity-fill {
            height: 100%;
            background: linear-gradient(90deg, #81C784, #4CAF50);
            border-radius: 10px;
        }
        .sources {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        .sources h3 {
            color: #2E7D32;
        }
        .sources ul {
            padding-left: 20px;
        }
        .sources li {
            margin-bottom: 8px;
        }
        .loading {
            text-align: center;
            padding: 20px;
            font-style: italic;
            color: #666;
        }
        .summary {
            background-color: #E8F5E9;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .guide-selector {
            margin-bottom: 20px;
        }
        .guide-selector select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        .compound-detail {
            padding: 15px;
            border-radius: 8px;
            background-color: #f5f5f5;
        }
        .compound-detail h3 {
            color: #2E7D32;
            margin-top: 0;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }
        .tab {
            padding: 12px 20px;
            cursor: pointer;
            background-color: #f1f1f1;
            border: 1px solid #ddd;
            border-bottom: none;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
        }
        .tab.active {
            background-color: #4CAF50;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .compound-properties {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .property-box {
            background: #e8f5e9;
            padding: 10px;
            border-radius: 5px;
        }
        .property-box h4 {
            margin: 0 0 5px 0;
            color: #2E7D32;
        }
        .mixes-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .mixes-table th, .mixes-table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        .mixes-table th {
            background-color: #4CAF50;
            color: white;
        }
        .mixes-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .mixes-table tr:hover {
            background-color: #e8f5e9;
        }
        .mix-actions {
            display: flex;
            gap: 5px;
        }
        .import-export {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .import-export input {
            flex: 1;
        }
        .example-mixes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .example-mix-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background-color: #f9f9f9;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .example-mix-card h3 {
            margin-top: 0;
            color: #2E7D32;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .example-mix-card.medical {
            border-top: 4px solid #FF9800;
        }
        .example-mix-card.recreational {
            border-top: 4px solid #9C27B0;
        }
        .example-mix-card ul {
            padding-left: 20px;
        }
        .example-mix-card li {
            margin-bottom: 8px;
        }
        .load-example-btn {
            margin-top: 15px;
        }
        .scheduler-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        .scheduler-form-full {
            grid-column: 1 / -1;
        }
        .schedule-results {
            margin-top: 20px;
        }
        .schedule-day {
            background: #f0f7ff;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0 5px 5px 0;
        }
        .schedule-day h4 {
            margin-top: 0;
            color: #0D47A1;
        }
        .dosage-instructions {
            background: #fff8e1;
            border-left: 4px solid #FFC107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }
        .dosage-instructions h3 {
            color: #FF8F00;
            margin-top: 0;
        }
        .warning-box {
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }
        .warning-box h3 {
            color: #b71c1c;
            margin-top: 0;
        }
        .schedule-summary {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .summary-box {
            background: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
        }
        .summary-box h4 {
            margin: 0 0 10px 0;
            color: #2E7D32;
        }
        .search-container {
            margin-bottom: 20px;
        }
        .search-bar {
            display: flex;
            gap: 10px;
        }
        .search-results {
            margin-top: 20px;
        }
        .result-item {
            background: #f0f7ff;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0 5px 5px 0;
        }
        .result-item h4 {
            margin-top: 0;
            color: #0D47A1;
        }
        .terpene-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        .terpene-tag {
            background: #E8F5E9;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 14px;
        }
        .dosage-guide {
            margin-top: 20px;
        }
        .dosage-category {
            margin-bottom: 30px;
        }
        .dosage-category h3 {
            color: #2E7D32;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .compound-dosage {
            background: #f9f9f9;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0 5px 5px 0;
        }
        .compound-dosage h4 {
            margin-top: 0;
            color: #1B5E20;
        }
        .dosage-ranges {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
        }
        .dosage-range {
            text-align: center;
            padding: 10px;
            background: #E8F5E9;
            border-radius: 5px;
            flex: 1;
            margin: 0 5px;
        }
        .dosage-range.low {
            background: #E3F2FD;
        }
        .dosage-range.medium {
            background: #FFF3E0;
        }
        .dosage-range.high {
            background: #FFEBEE;
        }
        .dosage-range h5 {
            margin: 0 0 5px 0;
            color: #2E7D32;
        }
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
            .scheduler-form {
                grid-template-columns: 1fr;
            }
            .dosage-ranges {
                flex-direction: column;
            }
            .dosage-range {
                margin: 5px 0;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>Cannabinoid & Terpene Effects Guide</h1>
        <p>Comprehensive reference for cannabinoid and terpene properties</p>
    </header>

    <div class="tabs">
        <div class="tab active" data-tab="calculator">Calculator</div>
        <div class="tab" data-tab="guide">Effects Guide</div>
        <div class="tab" data-tab="examples">Example Mixes</div>
        <div class="tab" data-tab="mixes">Saved Mixes</div>
        <div class="tab" data-tab="scheduler">Dosage Scheduler</div>
        <div class="tab" data-tab="search">Terpene Search</div>
        <div class="tab" data-tab="dosage">Dosage Guide</div>
        <div class="tab" data-tab="dose-calculator">Dose Calculator</div>
        <div class="tab" data-tab="percentage-converter">Percentage Converter</div>
    </div>

    <div class="container">
        <section class="input-section tab-content active" id="calculator-tab">
            <h2>Dosage Input</h2>
            <form id="calculator-form">
                <div class="compound-group">
                    <h3>Cannabinoids (mg)</h3>
                    <div class="compound-grid" id="cannabinoids-container">
                        <!-- Cannabinoids will be populated by JavaScript -->
                    </div>
                </div>
                
                <div class="compound-group">
                    <h3>Terpenes (mg)</h3>
                    <div class="compound-grid" id="terpenes-container">
                        <!-- Terpenes will be populated by JavaScript -->
                    </div>
                </div>
                
                <div style="display: flex; gap: 10px;">
                    <button type="submit">Calculate Effects</button>
                    <button type="button" id="save-mix-btn" class="btn-secondary">Save Current Mix</button>
                </div>
            </form>
        </section>
        
        <section class="results-section tab-content active" id="results-tab">
            <h2>Results</h2>
            <div class="results-content" id="results-content">
                <p>Enter your cannabinoid and terpene dosages and click "Calculate Effects" to see potential effects.</p>
            </div>
        </section>
        
        <section class="guide-section tab-content" id="guide-tab">
            <h2>Effects Guide</h2>
            <div class="guide-content">
                <div class="guide-selector">
                    <select id="compound-selector">
                        <option value="">Select a compound to view details</option>
                        <!-- Options will be populated by JavaScript -->
                    </select>
                </div>
                <div class="compound-detail" id="compound-detail">
                    <p>Select a compound from the dropdown to view its effects and properties.</p>
                </div>
            </div>
        </section>
        
        <section class="examples-section tab-content" id="examples-tab">
            <h2>Example Mixes</h2>
            <div class="examples-content">
                <p>Explore these pre-made cannabinoid and terpene mixes designed for specific medical conditions and recreational experiences. Click "Load Mix" to try any example in the calculator.</p>
                
                <h3>Medical Mixes</h3>
                <div class="example-mixes-grid" id="medical-mixes-container">
                    <!-- Medical mixes will be populated by JavaScript -->
                </div>
                
                <h3 style="margin-top: 30px;">Recreational Mixes</h3>
                <div class="example-mixes-grid" id="recreational-mixes-container">
                    <!-- Recreational mixes will be populated by JavaScript -->
                </div>
            </div>
        </section>
        
        <section class="mixes-section tab-content" id="mixes-tab">
            <h2>Saved Mixes</h2>
            <div class="mixes-content">
                <div class="import-export">
                    <input type="file" id="import-file" accept=".json">
                    <button id="import-btn" class="btn-secondary">Import Mixes</button>
                    <button id="export-btn">Export All Mixes</button>
                </div>
                
                <table class="mixes-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Date Saved</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="mixes-table-body">
                        <!-- Mixes will be populated by JavaScript -->
                    </tbody>
                </table>
                
                <div id="no-mixes-message">
                    <p>You haven't saved any mixes yet. Create a mix in the Calculator tab and click "Save Current Mix".</p>
                </div>
            </div>
        </section>
        
        <section class="scheduler-section tab-content" id="scheduler-tab">
            <h2>Dosage Scheduler</h2>
            <div class="scheduler-content">
                <div class="scheduler-form">
                    <div>
                        <label for="scheduler-mix-select">Select Saved Mix:</label>
                        <select id="scheduler-mix-select">
                            <option value="">Choose a mix...</option>
                            <!-- Options will be populated by JavaScript -->
                        </select>
                    </div>
                    
                    <div>
                        <label for="daily-dosage">Daily Dosage (mg):</label>
                        <input type="number" id="daily-dosage" min="1" step="1" value="50">
                    </div>
                    
                    <div>
                        <label for="schedule-days">Schedule Duration (days):</label>
                        <input type="number" id="schedule-days" min="1" max="30" value="7">
                    </div>
                    
                    <div>
                        <label for="schedule-type">Schedule Type:</label>
                        <select id="schedule-type">
                            <option value="consistent">Consistent Dosage</option>
                            <option value="tapering">Tapering Schedule</option>
                            <option value="cycling">Cycling Schedule</option>
                        </select>
                    </div>
                    
                    <div class="scheduler-form-full">
                        <button id="generate-schedule-btn">Generate Dosage Schedule</button>
                    </div>
                </div>
                
                <div id="schedule-results" style="display: none;">
                    <h3>Dosage Schedule for <span id="schedule-mix-name"></span></h3>
                    
                    <div class="schedule-summary">
                        <div class="summary-box">
                            <h4>Total Duration</h4>
                            <p id="schedule-duration"></p>
                        </div>
                        <div class="summary-box">
                            <h4>Average Daily Dosage</h4>
                            <p id="average-dosage"></p>
                        </div>
                        <div class="summary-box">
                            <h4>Schedule Type</h4>
                            <p id="schedule-type-display"></p>
                        </div>
                    </div>
                    
                    <div class="dosage-instructions">
                        <h3>Usage Instructions</h3>
                        <p id="dosage-instructions-text"></p>
                    </div>
                    
                    <div class="warning-box">
                        <h3>Important Safety Information</h3>
                        <p>This schedule is for educational purposes only and should not replace professional medical advice. Start with lower doses and gradually increase as needed. Consult with a healthcare provider before using cannabinoid products, especially if you have underlying health conditions or are taking medications.</p>
                    </div>
                    
                    <div id="schedule-days-container">
                        <!-- Schedule days will be populated by JavaScript -->
                    </div>
                </div>
                
                <div id="no-saved-mixes-message" style="display: none;">
                    <p>You don't have any saved mixes yet. Please save a mix in the Calculator tab first, then return here to create a dosage schedule.</p>
                </div>
            </div>
        </section>
        
        <section class="search-section tab-content" id="search-tab">
            <h2>Terpene Search</h2>
            <div class="search-content">
                <div class="search-container">
                    <p>Search for medical conditions, symptoms, or desired effects to find the most effective terpenes:</p>
                    <div class="search-bar">
                        <input type="text" id="search-input" placeholder="e.g., chronic pain, anxiety, euphoria, sleep...">
                        <button id="search-btn">Search</button>
                    </div>
                </div>
                
                <div class="search-results" id="search-results">
                    <p>Enter a search term above to find relevant terpenes.</p>
                </div>
            </div>
        </section>
        
        <section class="dosage-section tab-content" id="dosage-tab">
            <h2>Dosage Guide</h2>
            <div class="dosage-content">
                <p>This guide provides recommended dosage ranges for cannabinoids and terpenes. These are general guidelines and individual responses may vary. Always start with lower doses and gradually increase as needed.</p>
                
                <div class="warning-box">
                    <h3>Important Safety Information</h3>
                    <p>These dosage recommendations are for educational purposes only and should not replace professional medical advice. Start with lower doses and gradually increase as needed. Consult with a healthcare provider before using cannabinoid products, especially if you have underlying health conditions or are taking medications.</p>
                </div>
                
                <div class="dosage-guide">
                    <div class="dosage-category">
                        <h3>Cannabinoids</h3>
                        <div id="cannabinoids-dosage-container">
                            <!-- Cannabinoid dosages will be populated by JavaScript -->
                        </div>
                    </div>
                    
                    <div class="dosage-category">
                        <h3>Terpenes</h3>
                        <div id="terpenes-dosage-container">
                            <!-- Terpene dosages will be populated by JavaScript -->
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <section class="dosage-section tab-content" id="dose-calculator-tab">
            <h2>Dose Calculator</h2>
            <div class="dosage-content">
                <div class="warning-box">
                    <h3>Important Safety Information</h3>
                    <p>This calculator is for educational purposes only and should not replace professional medical advice. Always consult with a healthcare provider before using cannabinoid products, especially if you have underlying health conditions or are taking medications.</p>
                </div>
                
                <div class="scheduler-form">
                    <div>
                        <label for="dose-unit">Unit of Measurement:</label>
                        <select id="dose-unit">
                            <option value="mg">Milligrams (mg)</option>
                            <option value="g">Grams (g)</option>
                        </select>
                    </div>
                    
                    <div>
                        <label for="dose-mix-select">Select Saved Mix:</label>
                        <select id="dose-mix-select">
                            <option value="">Choose a mix...</option>
                            <!-- Options will be populated by JavaScript -->
                        </select>
                    </div>
                    
                    <div>
                        <label for="total-quantity">Total Quantity:</label>
                        <input type="number" id="total-quantity" min="0" step="0.1" value="0">
                    </div>
                    
                    <div>
                        <label for="dose-size">Dose Size:</label>
                        <input type="number" id="dose-size" min="0" step="0.1" value="0">
                    </div>
                    
                    <div class="scheduler-form-full">
                        <button id="calculate-doses-btn">Calculate Number of Doses</button>
                    </div>
                </div>
                
                <div id="dose-results" style="display: none; margin-top: 20px;">
                    <h3>Dose Calculation Results</h3>
                    <div class="summary-box">
                        <h4>Selected Mix</h4>
                        <p id="selected-mix-name"></p>
                    </div>
                    <div class="summary-box">
                        <h4>Total Quantity</h4>
                        <p id="total-quantity-result"></p>
                    </div>
                    <div class="summary-box">
                        <h4>Dose Size</h4>
                        <p id="dose-size-result"></p>
                    </div>
                    <div class="summary-box">
                        <h4>Number of Doses</h4>
                        <p id="number-of-doses" style="font-size: 1.5em; font-weight: bold; color: #4CAF50;"></p>
                    </div>
                </div>
                
                <div id="no-saved-mixes-dose-message" style="display: none;">
                    <p>You don't have any saved mixes yet. Please save a mix in the Calculator tab first, then return here to calculate doses.</p>
                </div>
            </div>
       </section>
       
       <section class="dosage-section tab-content" id="percentage-converter-tab">
           <h2>Percentage Converter</h2>
           <div class="dosage-content">
               <div class="warning-box">
                   <h3>Important Information</h3>
                   <p>This converter helps you calculate the actual milligram values of cannabinoids and terpenes based on their percentage concentrations in a given quantity of material.</p>
               </div>
               
               <div class="scheduler-form">
                   <div>
                       <label for="total-quantity-percentage">Total Quantity:</label>
                       <input type="number" id="total-quantity-percentage" min="0" step="0.1" value="0">
                   </div>
                   
                   <div>
                       <label for="unit-selector">Unit:</label>
                       <select id="unit-selector">
                           <option value="mg">Milligrams (mg)</option>
                           <option value="g">Grams (g)</option>
                       </select>
                   </div>
                   
                   <div class="scheduler-form-full">
                       <button id="calculate-percentages-btn">Calculate Milligram Values</button>
                   </div>
               </div>
               
               <div class="compound-group">
                   <h3>Cannabinoids (%)</h3>
                   <div class="compound-grid" id="cannabinoids-percentage-container">
                       <!-- Cannabinoids will be populated by JavaScript -->
                   </div>
               </div>
               
               <div class="compound-group">
                   <h3>Terpenes (%)</h3>
                   <div class="compound-grid" id="terpenes-percentage-container">
                       <!-- Terpenes will be populated by JavaScript -->
                   </div>
               </div>
               
               <div id="percentage-results" style="display: none; margin-top: 20px;">
                   <h3>Calculated Milligram Values</h3>
                   <div class="summary-box">
                       <h4>Total Quantity</h4>
                       <p id="total-quantity-result-percentage"></p>
                   </div>
                   
                   <div class="compound-group">
                       <h3>Cannabinoids (mg)</h3>
                       <div class="compound-grid" id="cannabinoids-mg-results">
                           <!-- Cannabinoid mg values will be populated by JavaScript -->
                       </div>
                   </div>
                   
                   <div class="compound-group">
                       <h3>Terpenes (mg)</h3>
                       <div class="compound-grid" id="terpenes-mg-results">
                           <!-- Terpene mg values will be populated by JavaScript -->
                       </div>
                   </div>
               </div>
           </div>
       </section>
   </div>

    <script>
        // Compound data
        const cannabinoids = ["CBG", "CBN", "CBD", "THC"];
        const terpenes = [
            "alpha-Bisabolol", "alpha-Caryophyllene", "alpha-Phellandrene", 
            "alpha-Pinene", "alpha-Terpinene", "alpha-Terpineol", 
            "beta-Caryophyllene", "beta-Myrcene", "beta-Phellandrene", 
            "beta-Pinene", "Camphene", "Caryophyllene-Oxide", 
            "Cedrene", "Citral", "Citronellol", "d-Camphor", 
            "d-Limonene", "Delta-3-Carene", "Farnesene", 
            "Fenchyl Alcohol", "gamma-Terpinene", "Geraniol", 
            "Guaiene", "Isoborneol", "L-Menthol", "Linalool", 
            "Nerol", "Sabinene", "Terpinolene", "Valencene"
        ];
        
        // All compounds list
        const allCompounds = [...cannabinoids, ...terpenes];
        
        // Compound database (embedded in JavaScript for offline access)
        const compoundDatabase = {{ compound_database | tojson }};
        
        // Example mixes
        const exampleMixes = {{ example_mixes | tojson }};
        
        // Saved mixes
        let savedMixes = JSON.parse(localStorage.getItem('cannabisMixes')) || [];
        
        // Terpene search database
        const terpeneSearchDatabase = {{ terpene_search_database | tojson }};
        
        // Dosage guide data
        const dosageGuide = {{ dosage_guide | tojson }};
        
        // Populate input fields
        function populateInputs() {
            const cannabinoidsContainer = document.getElementById('cannabinoids-container');
            const terpenesContainer = document.getElementById('terpenes-container');
            const compoundSelector = document.getElementById('compound-selector');
            const schedulerMixSelect = document.getElementById('scheduler-mix-select');
            
            cannabinoids.forEach(name => {
                const item = document.createElement('div');
                item.className = 'compound-item';
                item.innerHTML = `
                    <label for="cannabinoid-${name}">${name}</label>
                    <input type="number" id="cannabinoid-${name}" name="cannabinoid-${name}" value="0" min="0" step="0.1">
                `;
                cannabinoidsContainer.appendChild(item);
                
                // Add to selector
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                compoundSelector.appendChild(option);
            });
            
            terpenes.forEach(name => {
                const item = document.createElement('div');
                item.className = 'compound-item';
                item.innerHTML = `
                    <label for="terpene-${name}">${name}</label>
                    <input type="number" id="terpene-${name}" name="terpene-${name}" value="0" min="0" step="0.1">
                `;
                terpenesContainer.appendChild(item);
                
                // Add to selector
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                compoundSelector.appendChild(option);
            });
            
            // Populate scheduler mix selector
            populateSchedulerMixes();
            
            // Populate dose calculator mix selector
            populateDoseCalculatorMixes();
        }
        
        // Populate scheduler mix selector
        function populateSchedulerMixes() {
            const schedulerMixSelect = document.getElementById('scheduler-mix-select');
            schedulerMixSelect.innerHTML = '<option value="">Choose a mix...</option>';
            
            if (savedMixes.length === 0) {
                document.getElementById('no-saved-mixes-message').style.display = 'block';
                document.getElementById('schedule-results').style.display = 'none';
                return;
            }
            
            document.getElementById('no-saved-mixes-message').style.display = 'none';
            
            savedMixes.forEach(mix => {
                const option = document.createElement('option');
                option.value = mix.id;
                option.textContent = mix.name;
                schedulerMixSelect.appendChild(option);
            });
        }
        
        // Populate dose calculator mix selector
        function populateDoseCalculatorMixes() {
            const doseMixSelect = document.getElementById('dose-mix-select');
            doseMixSelect.innerHTML = '<option value="">Choose a mix...</option>';
            
            if (savedMixes.length === 0) {
                document.getElementById('no-saved-mixes-dose-message').style.display = 'block';
                document.getElementById('dose-results').style.display = 'none';
                return;
            }
            
            document.getElementById('no-saved-mixes-dose-message').style.display = 'none';
            
            savedMixes.forEach(mix => {
                const option = document.createElement('option');
                option.value = mix.id;
                option.textContent = mix.name;
                doseMixSelect.appendChild(option);
            });
        }
        
        // Handle form submission
        document.getElementById('calculator-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading message
            document.getElementById('results-content').innerHTML = '<div class="loading">Calculating effects... Searching research databases...</div>';
            
            // Collect form data
            const formData = new FormData(this);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = parseFloat(value) || 0;
            }
            
            // Send to server
            fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                document.getElementById('results-content').innerHTML = 
                    '<p style="color: red;">Error calculating effects. Please try again.</p>';
                console.error('Error:', error);
            });
        });
        
        // Save current mix
        document.getElementById('save-mix-btn').addEventListener('click', function() {
            // Collect current values
            const mix = {};
            cannabinoids.forEach(name => {
                const value = document.getElementById(`cannabinoid-${name}`).value;
                if (value && parseFloat(value) > 0) {
                    mix[`cannabinoid-${name}`] = parseFloat(value);
                }
            });
            
            terpenes.forEach(name => {
                const value = document.getElementById(`terpene-${name}`).value;
                if (value && parseFloat(value) > 0) {
                    mix[`terpene-${name}`] = parseFloat(value);
                }
            });
            
            // Check if mix has any values
            if (Object.keys(mix).length === 0) {
                alert('Please enter at least one non-zero value before saving.');
                return;
            }
            
            // Get name for mix
            const name = prompt('Enter a name for this mix:', `Mix ${savedMixes.length + 1}`);
            if (!name) return;
            
            // Save mix
            const mixEntry = {
                id: Date.now(),
                name: name,
                date: new Date().toISOString(),
                mix: mix
            };
            
            savedMixes.push(mixEntry);
            localStorage.setItem('cannabisMixes', JSON.stringify(savedMixes));
            
            // Update scheduler mix selector
            populateSchedulerMixes();
            
            alert('Mix saved successfully!');
        });
        
        // Calculate doses functionality
        document.getElementById('calculate-doses-btn').addEventListener('click', function() {
            const mixId = document.getElementById('dose-mix-select').value;
            const unit = document.getElementById('dose-unit').value;
            const totalQuantity = parseFloat(document.getElementById('total-quantity').value);
            const doseSize = parseFloat(document.getElementById('dose-size').value);
            
            if (!mixId) {
                alert('Please select a saved mix.');
                return;
            }
            
            if (isNaN(totalQuantity) || totalQuantity <= 0) {
                alert('Please enter a valid total quantity.');
                return;
            }
            
            if (isNaN(doseSize) || doseSize <= 0) {
                alert('Please enter a valid dose size.');
                return;
            }
            
            const mix = savedMixes.find(m => m.id == mixId);
            if (!mix) {
                alert('Selected mix not found.');
                return;
            }
            
            // Convert units if necessary
            let convertedTotalQuantity = totalQuantity;
            let convertedDoseSize = doseSize;
            let unitLabel = 'mg';
            
            if (unit === 'g') {
                convertedTotalQuantity = totalQuantity * 1000; // Convert grams to mg
                convertedDoseSize = doseSize * 1000; // Convert grams to mg
                unitLabel = 'g';
            }
            
            // Calculate number of doses
            const numberOfDoses = Math.floor(convertedTotalQuantity / convertedDoseSize);
            
            // Display results
            document.getElementById('selected-mix-name').textContent = mix.name;
            document.getElementById('total-quantity-result').textContent = `${totalQuantity} ${unitLabel}`;
            document.getElementById('dose-size-result').textContent = `${doseSize} ${unitLabel}`;
            document.getElementById('number-of-doses').textContent = numberOfDoses;
            
            document.getElementById('dose-results').style.display = 'block';
        });
        
        // Display results
        function displayResults(data) {
            const resultsContent = document.getElementById('results-content');
            
            let html = `
                <div class="summary">
                    <h3>Profile Summary</h3>
                    <p><strong>Dominant Cannabinoid:</strong> ${data.dominant_cannabinoid || 'None'}</p>
                    <p><strong>Dominant Terpene:</strong> ${data.dominant_terpene || 'None'}</p>
                </div>
                
                <h3>Medical Effects</h3>
            `;
            
            // Sort and display medical effects
            const sortedMedical = Object.entries(data.medical_effects).sort((a, b) => b[1] - a[1]);
            sortedMedical.forEach(([effect, intensity]) => {
                const percentage = Math.min(100, Math.round(intensity * 100));
                html += `
                    <div class="effect-item">
                        <div class="effect-name">${effect}</div>
                        <div class="intensity-bar">
                            <div class="intensity-fill" style="width: ${percentage}%"></div>
                        </div>
                        <div>Intensity: ${intensity.toFixed(2)}</div>
                    </div>
                `;
            });
            
            html += `<h3>Recreational Effects</h3>`;
            
            // Sort and display recreational effects
            const sortedRecreational = Object.entries(data.recreational_effects).sort((a, b) => b[1] - a[1]);
            sortedRecreational.forEach(([effect, intensity]) => {
                const percentage = Math.min(100, Math.round(intensity * 100));
                html += `
                    <div class="effect-item">
                        <div class="effect-name">${effect}</div>
                        <div class="intensity-bar">
                            <div class="intensity-fill" style="width: ${percentage}%"></div>
                        </div>
                        <div>Intensity: ${intensity.toFixed(2)}</div>
                    </div>
                `;
            });
            
            // Display sources
            html += `
                <div class="sources">
                    <h3>Research Sources</h3>
                    <ul>
            `;
            
            data.sources.forEach(source => {
                html += `<li><a href="${source}" target="_blank">${source}</a></li>`;
            });
            
            html += `
                    </ul>
                </div>
                <p><em>Note: This calculation is based on simplified models and should not replace professional medical advice.</em></p>
            `;
            
            resultsContent.innerHTML = html;
        }
        
        // Display compound details (now using embedded database)
        function displayCompoundDetail(compound) {
            const data = compoundDatabase[compound];
            const detailDiv = document.getElementById('compound-detail');
            
            if (!data) {
                detailDiv.innerHTML = '<p>No information available for this compound.</p>';
                return;
            }
            
            let html = `
                <h3>${compound}</h3>
                <div class="compound-properties">
                    <div class="property-box">
                        <h4>Chemical Class</h4>
                        <p>${data.chemical_class}</p>
                    </div>
                    <div class="property-box">
                        <h4>Molecular Formula</h4>
                        <p>${data.molecular_formula}</p>
                    </div>
                    <div class="property-box">
                        <h4>Molar Mass</h4>
                        <p>${data.molar_mass} g/mol</p>
                    </div>
                    <div class="property-box">
                        <h4>Boiling Point</h4>
                        <p>${data.boiling_point}</p>
                    </div>
                </div>
                
                <h4>Pharmacological Properties:</h4>
                <p>${data.pharmacology}</p>
                
                <h4>Therapeutic Indications:</h4>
                <ul>
            `;
            
            data.therapeutic_indications.forEach(indication => {
                html += `<li>${indication}</li>`;
            });
            
            html += `
                </ul>
                
                <h4>Subjective Effects:</h4>
                <ul>
            `;
            
            data.subjective_effects.forEach(effect => {
                html += `<li>${effect}</li>`;
            });
            
            html += `
                </ul>
                
                <div class="sources">
                    <h4>Research Sources:</h4>
                    <ul>
            `;
            
            data.sources.forEach(source => {
                html += `<li><a href="${source}" target="_blank">${source}</a></li>`;
            });
            
            html += `
                    </ul>
                </div>
            `;
            
            detailDiv.innerHTML = html;
        }
        
        // Display example mixes
        function displayExampleMixes() {
            const medicalContainer = document.getElementById('medical-mixes-container');
            const recreationalContainer = document.getElementById('recreational-mixes-container');
            
            // Clear containers
            medicalContainer.innerHTML = '';
            recreationalContainer.innerHTML = '';
            
            // Filter mixes
            const medicalMixes = exampleMixes.filter(mix => mix.type === 'medical');
            const recreationalMixes = exampleMixes.filter(mix => mix.type === 'recreational');
            
            // Display medical mixes
            medicalMixes.forEach(mix => {
                const card = document.createElement('div');
                card.className = 'example-mix-card medical';
                card.innerHTML = `
                    <h3>${mix.name}</h3>
                    <p><strong>Target:</strong> ${mix.target}</p>
                    <p>${mix.description}</p>
                    <h4>Composition:</h4>
                    <ul>
                        ${Object.entries(mix.mix).map(([key, value]) => `<li>${key.replace('cannabinoid-', '').replace('terpene-', '')}: ${value}mg</li>`).join('')}
                    </ul>
                    <button class="btn-medical load-example-btn" data-index="${exampleMixes.indexOf(mix)}">Load Mix</button>
                `;
                medicalContainer.appendChild(card);
            });
            
            // Display recreational mixes
            recreationalMixes.forEach(mix => {
                const card = document.createElement('div');
                card.className = 'example-mix-card recreational';
                card.innerHTML = `
                    <h3>${mix.name}</h3>
                    <p><strong>Experience:</strong> ${mix.target}</p>
                    <p>${mix.description}</p>
                    <h4>Composition:</h4>
                    <ul>
                        ${Object.entries(mix.mix).map(([key, value]) => `<li>${key.replace('cannabinoid-', '').replace('terpene-', '')}: ${value}mg</li>`).join('')}
                    </ul>
                    <button class="btn-recreational load-example-btn" data-index="${exampleMixes.indexOf(mix)}">Load Mix</button>
                `;
                recreationalContainer.appendChild(card);
            });
            
            // Add event listeners to load buttons
            document.querySelectorAll('.load-example-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const index = parseInt(this.getAttribute('data-index'));
                    loadExampleMix(index);
                });
            });
        }
        
        // Load an example mix
        function loadExampleMix(index) {
            const mix = exampleMixes[index];
            if (!mix) return;
            
            // Reset all inputs to 0
            cannabinoids.forEach(name => {
                document.getElementById(`cannabinoid-${name}`).value = 0;
            });
            
            terpenes.forEach(name => {
                document.getElementById(`terpene-${name}`).value = 0;
            });
            
            // Set values from mix
            Object.keys(mix.mix).forEach(key => {
                const element = document.getElementById(key);
                if (element) {
                    element.value = mix.mix[key];
                }
            });
            
            // Switch to calculator tab
            switchTab('calculator');
            
            alert(`Example mix "${mix.name}" loaded successfully!`);
        }
        
        // Display saved mixes
        function displaySavedMixes() {
            const tbody = document.getElementById('mixes-table-body');
            const noMixesMessage = document.getElementById('no-mixes-message');
            
            if (savedMixes.length === 0) {
                tbody.innerHTML = '';
                noMixesMessage.style.display = 'block';
                return;
            }
            
            noMixesMessage.style.display = 'none';
            tbody.innerHTML = '';
            
            savedMixes.forEach(mix => {
                const row = document.createElement('tr');
                
                // Format date
                const date = new Date(mix.date);
                const formattedDate = date.toLocaleString();
                
                row.innerHTML = `
                    <td>${mix.name}</td>
                    <td>${formattedDate}</td>
                    <td class="mix-actions">
                        <button class="btn-secondary load-mix-btn" data-id="${mix.id}">Load</button>
                        <button class="btn-danger delete-mix-btn" data-id="${mix.id}">Delete</button>
                    </td>
                `;
                
                tbody.appendChild(row);
            });
            
            // Add event listeners to action buttons
            document.querySelectorAll('.load-mix-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const id = parseInt(this.getAttribute('data-id'));
                    loadMix(id);
                });
            });
            
            document.querySelectorAll('.delete-mix-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const id = parseInt(this.getAttribute('data-id'));
                    deleteMix(id);
                });
            });
            
            // Update scheduler mix selector
            populateSchedulerMixes();
        }
        
        // Load a mix
        function loadMix(id) {
            const mixEntry = savedMixes.find(m => m.id === id);
            if (!mixEntry) return;
            
            // Reset all inputs to 0
            cannabinoids.forEach(name => {
                document.getElementById(`cannabinoid-${name}`).value = 0;
            });
            
            terpenes.forEach(name => {
                document.getElementById(`terpene-${name}`).value = 0;
            });
            
            // Set values from mix
            Object.keys(mixEntry.mix).forEach(key => {
                const element = document.getElementById(key);
                if (element) {
                    element.value = mixEntry.mix[key];
                }
            });
            
            // Switch to calculator tab
            switchTab('calculator');
            
            alert(`Mix "${mixEntry.name}" loaded successfully!`);
        }
        
        // Delete a mix
        function deleteMix(id) {
            if (!confirm('Are you sure you want to delete this mix?')) return;
            
            savedMixes = savedMixes.filter(m => m.id !== id);
            localStorage.setItem('cannabisMixes', JSON.stringify(savedMixes));
            displaySavedMixes();
        }
        
        // Export all mixes
        document.getElementById('export-btn').addEventListener('click', function() {
            if (savedMixes.length === 0) {
                alert('No mixes to export.');
                return;
            }
            
            const dataStr = JSON.stringify(savedMixes, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = 'cannabis-mixes.json';
            link.click();
        });
        
        // Import mixes
        document.getElementById('import-btn').addEventListener('click', function() {
            const fileInput = document.getElementById('import-file');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a file to import.');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const importedMixes = JSON.parse(e.target.result);
                    
                    // Validate imported data
                    if (!Array.isArray(importedMixes)) {
                        throw new Error('Invalid file format.');
                    }
                    
                    // Merge with existing mixes (avoid duplicates)
                    importedMixes.forEach(newMix => {
                        // Check if mix with same ID already exists
                        const exists = savedMixes.some(m => m.id === newMix.id);
                        if (!exists) {
                            savedMixes.push(newMix);
                        }
                    });
                    
                    localStorage.setItem('cannabisMixes', JSON.stringify(savedMixes));
                    displaySavedMixes();
                    fileInput.value = ''; // Reset file input
                    alert('Mixes imported successfully!');
                } catch (error) {
                    alert('Error importing mixes: ' + error.message);
                }
            };
            
            reader.readAsText(file);
        });
        
        // Generate dosage schedule
        document.getElementById('generate-schedule-btn').addEventListener('click', function() {
            const mixId = document.getElementById('scheduler-mix-select').value;
            const dailyDosage = parseFloat(document.getElementById('daily-dosage').value);
            const scheduleDays = parseInt(document.getElementById('schedule-days').value);
            const scheduleType = document.getElementById('schedule-type').value;
            
            if (!mixId) {
                alert('Please select a saved mix.');
                return;
            }
            
            if (isNaN(dailyDosage) || dailyDosage <= 0) {
                alert('Please enter a valid daily dosage.');
                return;
            }
            
            if (isNaN(scheduleDays) || scheduleDays <= 0) {
                alert('Please enter a valid schedule duration.');
                return;
            }
            
            const mix = savedMixes.find(m => m.id == mixId);
            if (!mix) {
                alert('Selected mix not found.');
                return;
            }
            
            generateSchedule(mix, dailyDosage, scheduleDays, scheduleType);
        });
        
        // Generate schedule based on type
        function generateSchedule(mix, dailyDosage, scheduleDays, scheduleType) {
            const scheduleResults = document.getElementById('schedule-results');
            const scheduleMixName = document.getElementById('schedule-mix-name');
            const scheduleDuration = document.getElementById('schedule-duration');
            const averageDosage = document.getElementById('average-dosage');
            const scheduleTypeDisplay = document.getElementById('schedule-type-display');
            const dosageInstructionsText = document.getElementById('dosage-instructions-text');
            const scheduleDaysContainer = document.getElementById('schedule-days-container');
            
            // Set header information
            scheduleMixName.textContent = mix.name;
            scheduleDuration.textContent = `${scheduleDays} days`;
            scheduleTypeDisplay.textContent = scheduleType === 'consistent' ? 'Consistent Dosage' : 
                                            scheduleType === 'tapering' ? 'Tapering Schedule' : 
                                            'Cycling Schedule';
            
            // Calculate average dosage
            let totalDosage = 0;
            const schedule = [];
            const startDate = new Date();
            
            // Generate schedule based on type
            if (scheduleType === 'consistent') {
                for (let i = 0; i < scheduleDays; i++) {
                    const dayDate = new Date(startDate);
                    dayDate.setDate(startDate.getDate() + i);
                    
                    schedule.push({
                        day: i + 1,
                        date: dayDate,
                        dosage: dailyDosage
                    });
                    totalDosage += dailyDosage;
                }
                averageDosage.textContent = `${dailyDosage.toFixed(1)} mg`;
                dosageInstructionsText.textContent = "Take the same dosage each day at the same time. Consistency helps maintain stable levels in your system.";
            } 
            else if (scheduleType === 'tapering') {
                // Start with higher dose and taper down
                const startDosage = dailyDosage * 1.5;
                const endDosage = dailyDosage * 0.5;
                const decrement = (startDosage - endDosage) / (scheduleDays - 1);
                
                for (let i = 0; i < scheduleDays; i++) {
                    const dayDate = new Date(startDate);
                    dayDate.setDate(startDate.getDate() + i);
                    
                    const dayDosage = startDosage - (i * decrement);
                    schedule.push({
                        day: i + 1,
                        date: dayDate,
                        dosage: Math.max(dayDosage, endDosage)
                    });
                    totalDosage += dayDosage;
                }
                averageDosage.textContent = `${(totalDosage / scheduleDays).toFixed(1)} mg`;
                dosageInstructionsText.textContent = "Start with a higher dose and gradually decrease over time. This approach may help with tolerance management.";
            } 
            else { // cycling
                // Alternate between higher and lower doses
                for (let i = 0; i < scheduleDays; i++) {
                    const dayDate = new Date(startDate);
                    dayDate.setDate(startDate.getDate() + i);
                    
                    const isHighDay = i % 2 === 0;
                    const dayDosage = isHighDay ? dailyDosage * 1.3 : dailyDosage * 0.7;
                    
                    schedule.push({
                        day: i + 1,
                        date: dayDate,
                        dosage: dayDosage
                    });
                    totalDosage += dayDosage;
                }
                averageDosage.textContent = `${(totalDosage / scheduleDays).toFixed(1)} mg`;
                dosageInstructionsText.textContent = "Alternate between higher and lower doses. This cycling approach may help prevent tolerance buildup.";
            }
            
            // Display schedule
            scheduleDaysContainer.innerHTML = '';
            schedule.forEach(day => {
                const dayElement = document.createElement('div');
                dayElement.className = 'schedule-day';
                dayElement.innerHTML = `
                    <h4>Day ${day.day} - ${day.date.toLocaleDateString()}</h4>
                    <p><strong>Dosage:</strong> ${day.dosage.toFixed(1)} mg</p>
                    <p><strong>Instructions:</strong> Take in the morning with or after food. Start with a smaller dose to assess tolerance.</p>
                `;
                scheduleDaysContainer.appendChild(dayElement);
            });
            
            // Show results
            scheduleResults.style.display = 'block';
        }
        
        // Terpene search functionality
        document.getElementById('search-btn').addEventListener('click', function() {
            performSearch();
        });
        
        document.getElementById('search-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        function performSearch() {
            const searchTerm = document.getElementById('search-input').value.toLowerCase().trim();
            const searchResults = document.getElementById('search-results');
            
            if (!searchTerm) {
                searchResults.innerHTML = '<p>Please enter a search term.</p>';
                return;
            }
            
            // Find matching terpenes
            const matches = [];
            
            for (const [terpene, data] of Object.entries(terpeneSearchDatabase)) {
                // Check if search term matches any keywords
                const allKeywords = [...data.medical_keywords, ...data.recreational_keywords].map(k => k.toLowerCase());
                if (allKeywords.some(keyword => keyword.includes(searchTerm) || searchTerm.includes(keyword))) {
                    matches.push({
                        terpene: terpene,
                         data
                    });
                }
            }
            
            // Display results
            if (matches.length === 0) {
                searchResults.innerHTML = `<p>No terpenes found for "${searchTerm}". Try a different search term.</p>`;
                return;
            }
            
            let html = `<h3>Terpenes for "${searchTerm}"</h3>`;
            
            matches.forEach(match => {
                const medicalKeywords = match.data.medical_keywords.join(', ');
                const recreationalKeywords = match.data.recreational_keywords.join(', ');
                
                html += `
                    <div class="result-item">
                        <h4>${match.terpene}</h4>
                        ${medicalKeywords ? `<p><strong>Medical benefits:</strong> ${medicalKeywords}</p>` : ''}
                        ${recreationalKeywords ? `<p><strong>Recreational effects:</strong> ${recreationalKeywords}</p>` : ''}
                        <div class="terpene-list">
                            <span class="terpene-tag">${match.terpene}</span>
                        </div>
                    </div>
                `;
            });
            
            searchResults.innerHTML = html;
        }
        
        // Display dosage guide
        function displayDosageGuide() {
            const cannabinoidsContainer = document.getElementById('cannabinoids-dosage-container');
            const terpenesContainer = document.getElementById('terpenes-dosage-container');
            
            // Clear containers
            cannabinoidsContainer.innerHTML = '';
            terpenesContainer.innerHTML = '';
            
            // Display cannabinoid dosages
            cannabinoids.forEach(cannabinoid => {
                const data = dosageGuide.cannabinoids[cannabinoid];
                if (!data) return;
                
                const element = document.createElement('div');
                element.className = 'compound-dosage';
                element.innerHTML = `
                    <h4>${cannabinoid}</h4>
                    <p>${data.description}</p>
                    <div class="dosage-ranges">
                        <div class="dosage-range low">
                            <h5>Low</h5>
                            <p>${data.low_dose}</p>
                        </div>
                        <div class="dosage-range medium">
                            <h5>Medium</h5>
                            <p>${data.medium_dose}</p>
                        </div>
                        <div class="dosage-range high">
                            <h5>High</h5>
                            <p>${data.high_dose}</p>
                        </div>
                    </div>
                `;
                cannabinoidsContainer.appendChild(element);
            });
            
            // Display terpene dosages
            terpenes.forEach(terpene => {
                const data = dosageGuide.terpenes[terpene];
                if (!data) return;
                
                const element = document.createElement('div');
                element.className = 'compound-dosage';
                element.innerHTML = `
                    <h4>${terpene}</h4>
                    <p>${data.description}</p>
                    <div class="dosage-ranges">
                        <div class="dosage-range low">
                            <h5>Low</h5>
                            <p>${data.low_dose}</p>
                        </div>
                        <div class="dosage-range medium">
                            <h5>Medium</h5>
                            <p>${data.medium_dose}</p>
                        </div>
                        <div class="dosage-range high">
                            <h5>High</h5>
                            <p>${data.high_dose}</p>
                        </div>
                    </div>
                `;
                terpenesContainer.appendChild(element);
            });
        }
        
        // Tab switching
        function switchTab(tabName) {
            // Remove active class from all tabs and content
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab
            document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');
            
            // Show corresponding content
            if (tabName === 'calculator') {
                document.getElementById('calculator-tab').classList.add('active');
                document.getElementById('results-tab').classList.add('active');
            } else if (tabName === 'guide') {
                document.getElementById('guide-tab').classList.add('active');
            } else if (tabName === 'examples') {
                document.getElementById('examples-tab').classList.add('active');
            } else if (tabName === 'mixes') {
                document.getElementById('mixes-tab').classList.add('active');
                displaySavedMixes(); // Refresh the mixes display
            } else if (tabName === 'scheduler') {
                document.getElementById('scheduler-tab').classList.add('active');
                populateSchedulerMixes(); // Refresh the scheduler mixes
            } else if (tabName === 'search') {
                document.getElementById('search-tab').classList.add('active');
            } else if (tabName === 'dosage') {
                document.getElementById('dosage-tab').classList.add('active');
                displayDosageGuide(); // Display dosage guide
            } else if (tabName === 'dose-calculator') {
                document.getElementById('dose-calculator-tab').classList.add('active');
                populateDoseCalculatorMixes(); // Refresh the dose calculator mixes
            } else if (tabName === 'percentage-converter') {
                document.getElementById('percentage-converter-tab').classList.add('active');
                populatePercentageInputs(); // Refresh the percentage converter inputs
            }
        }
        
        // Tab switching event listeners
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.getAttribute('data-tab');
                switchTab(tabName);
            });
        });
        
        // Compound selector change
        document.getElementById('compound-selector').addEventListener('change', function() {
            const selectedCompound = this.value;
            if (selectedCompound) {
                displayCompoundDetail(selectedCompound);
            } else {
                document.getElementById('compound-detail').innerHTML = 
                    '<p>Select a compound from the dropdown to view its effects and properties.</p>';
            }
        });
        
        // Populate percentage converter inputs
        function populatePercentageInputs() {
            const cannabinoidsContainer = document.getElementById('cannabinoids-percentage-container');
            const terpenesContainer = document.getElementById('terpenes-percentage-container');
            
            // Clear containers
            cannabinoidsContainer.innerHTML = '';
            terpenesContainer.innerHTML = '';
            
            cannabinoids.forEach(name => {
                const item = document.createElement('div');
                item.className = 'compound-item';
                item.innerHTML = `
                    <label for="percentage-cannabinoid-${name}">${name} (%)</label>
                    <input type="number" id="percentage-cannabinoid-${name}" name="percentage-cannabinoid-${name}" value="0" min="0" step="0.01" max="100">
                `;
                cannabinoidsContainer.appendChild(item);
            });
            
            terpenes.forEach(name => {
                const item = document.createElement('div');
                item.className = 'compound-item';
                item.innerHTML = `
                    <label for="percentage-terpene-${name}">${name} (%)</label>
                    <input type="number" id="percentage-terpene-${name}" name="percentage-terpene-${name}" value="0" min="0" step="0.01" max="100">
                `;
                terpenesContainer.appendChild(item);
            });
        }
        
        // Calculate percentage values
        document.getElementById('calculate-percentages-btn').addEventListener('click', function() {
            const totalQuantity = parseFloat(document.getElementById('total-quantity-percentage').value);
            const unit = document.getElementById('unit-selector').value;
            
            if (isNaN(totalQuantity) || totalQuantity <= 0) {
                alert('Please enter a valid total quantity.');
                return;
            }
            
            // Convert to mg if needed
            let totalQuantityMg = totalQuantity;
            if (unit === 'g') {
                totalQuantityMg = totalQuantity * 1000;
            }
            
            // Display total quantity result
            document.getElementById('total-quantity-result-percentage').textContent =
                `${totalQuantity} ${unit} (${totalQuantityMg} mg)`;
            
            // Calculate and display cannabinoid mg values
            const cannabinoidsResultsContainer = document.getElementById('cannabinoids-mg-results');
            cannabinoidsResultsContainer.innerHTML = '';
            
            cannabinoids.forEach(name => {
                const percentage = parseFloat(document.getElementById(`percentage-cannabinoid-${name}`).value) || 0;
                const mgValue = (percentage / 100) * totalQuantityMg;
                
                const item = document.createElement('div');
                item.className = 'compound-item';
                item.innerHTML = `
                    <label for="result-cannabinoid-${name}">${name}</label>
                    <input type="text" id="result-cannabinoid-${name}" value="${mgValue.toFixed(2)} mg" readonly>
                `;
                cannabinoidsResultsContainer.appendChild(item);
            });
            
            // Calculate and display terpene mg values
            const terpenesResultsContainer = document.getElementById('terpenes-mg-results');
            terpenesResultsContainer.innerHTML = '';
            
            terpenes.forEach(name => {
                const percentage = parseFloat(document.getElementById(`percentage-terpene-${name}`).value) || 0;
                const mgValue = (percentage / 100) * totalQuantityMg;
                
                const item = document.createElement('div');
                item.className = 'compound-item';
                item.innerHTML = `
                    <label for="result-terpene-${name}">${name}</label>
                    <input type="text" id="result-terpene-${name}" value="${mgValue.toFixed(2)} mg" readonly>
                `;
                terpenesResultsContainer.appendChild(item);
            });
            
            // Show results
            document.getElementById('percentage-results').style.display = 'block';
        });
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            populateInputs();
            populatePercentageInputs();
            displaySavedMixes();
            displayExampleMixes();
        });
    </script>
</body>
</html>
'''

# Comprehensive compound database
COMPOUND_DATABASE = {
    "THC": {
        "chemical_class": "Cannabinoid",
        "molecular_formula": "C₂₁H₃₀O₂",
        "molar_mass": "314.46",
        "boiling_point": "157 °C (315 °F)",
        "pharmacology": "Partial agonist at CB1 and CB2 receptors. Modulates neurotransmitter release, particularly dopamine and GABA. Produces psychoactive effects through CB1 receptor activation in the central nervous system.",
        "therapeutic_indications": [
            "Chronic pain management",
            "Chemotherapy-induced nausea and vomiting",
            "Appetite stimulation in wasting syndromes",
            "Muscle spasticity in multiple sclerosis",
            "Glaucoma (intraocular pressure reduction)",
            "Post-traumatic stress disorder"
        ],
        "subjective_effects": [
            "Euphoria",
            "Relaxation",
            "Altered perception of time",
            "Enhanced sensory perception",
            "Increased appetite",
            "Mood enhancement"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7037009/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "CBD": {
        "chemical_class": "Cannabinoid",
        "molecular_formula": "C₂₁H₃₀O₂",
        "molar_mass": "314.46",
        "boiling_point": "160-180 °C (320-356 °F)",
        "pharmacology": "Antagonist at CB1 and CB2 receptors. Modulates serotonin receptors (5-HT1A), vanilloid receptors (TRPV1), and GPR55. Exhibits neuroprotective, anti-inflammatory, and anxiolytic properties without significant psychoactivity.",
        "therapeutic_indications": [
            "Epilepsy (Dravet syndrome, Lennox-Gastaut syndrome)",
            "Anxiety disorders",
            "Inflammatory conditions",
            "Neurodegenerative diseases",
            "Psychosis associated with substance use",
            "Cardiovascular health support"
        ],
        "subjective_effects": [
            "Calming effect",
            "Mental clarity",
            "Relaxation without intoxication",
            "Stress reduction",
            "Improved focus"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4808637/"
        ]
    },
    "CBG": {
        "chemical_class": "Cannabinoid",
        "molecular_formula": "C₂₁H₃₄O₂",
        "molar_mass": "318.49",
        "boiling_point": "Not established",
        "pharmacology": "Low-affinity antagonist at CB1 and CB2 receptors. Acts as an α2-adrenoceptor agonist and 5-HT1A receptor antagonist. Exhibits antibacterial properties and promotes neurogenesis.",
        "therapeutic_indications": [
            "Anti-inflammatory conditions",
            "Neuroprotection",
            "Antibacterial infections",
            "Glaucoma management",
            "Bone growth promotion",
            "Cancer research applications"
        ],
        "subjective_effects": [
            "Focus enhancement",
            "Mild energy boost",
            "Mental clarity",
            "Balanced mood"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/"
        ]
    },
    "CBN": {
        "chemical_class": "Cannabinoid",
        "molecular_formula": "C₂₁H₂₆O₂",
        "molar_mass": "310.43",
        "boiling_point": "Not established",
        "pharmacology": "Partial agonist at CB1 and CB2 receptors with lower psychoactivity than THC. Promotes bone cell growth and exhibits sedative properties through interaction with GABA receptors.",
        "therapeutic_indications": [
            "Sleep disorders",
            "Antibacterial applications",
            "Appetite stimulation",
            "Bone fracture healing",
            "Anti-inflammatory conditions",
            "Neuroprotection"
        ],
        "subjective_effects": [
            "Deep relaxation",
            "Sleep promotion",
            "Pain relief",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/"
        ]
    },
    "beta-Myrcene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "168 °C (334 °F)",
        "pharmacology": "Sedative and anti-inflammatory agent. Enhances transdermal absorption. Modulates opioid and cannabinoid receptor activity. Exhibits antioxidant properties through free radical scavenging.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Pain management",
            "Sleep disorders",
            "Antioxidant support",
            "Antimutagenic applications",
            "Cancer research"
        ],
        "subjective_effects": [
            "Enhanced relaxation",
            "Increased analgesic effects",
            "Sedation promotion",
            "Pain relief"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "d-Limonene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "176 °C (349 °F)",
        "pharmacology": "Monocyclic monoterpene with anxiolytic and antidepressant properties. Inhibits GABA transaminase and exhibits gastroprotective effects. Enhances dermal penetration and has antifungal properties.",
        "therapeutic_indications": [
            "Anxiety disorders",
            "Depression",
            "Fungal infections",
            "Gastric acid reduction",
            "Cancer research",
            "Inflammatory conditions"
        ],
        "subjective_effects": [
            "Uplifted mood",
            "Stress relief",
            "Enhanced focus",
            "Mental clarity"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "alpha-Pinene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "156 °C (313 °F)",
        "pharmacology": "Bicyclic monoterpene with bronchodilatory effects. Inhibits acetylcholinesterase, enhancing memory retention. Exhibits anti-inflammatory and antibacterial properties through multiple mechanisms.",
        "therapeutic_indications": [
            "Respiratory conditions",
            "Anti-inflammatory disorders",
            "Memory enhancement",
            "Bacterial infections",
            "Fungal infections",
            "Inflammatory bowel disease"
        ],
        "subjective_effects": [
            "Increased alertness",
            "Focus enhancement",
            "Respiratory support",
            "Mental clarity"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "beta-Pinene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "164 °C (327 °F)",
        "pharmacology": "Isomer of alpha-pinene with similar pharmacological properties. Bronchodilator and anti-inflammatory agent. Inhibits acetylcholinesterase and exhibits antimicrobial activity.",
        "therapeutic_indications": [
            "Respiratory conditions",
            "Anti-inflammatory disorders",
            "Memory enhancement",
            "Bacterial infections",
            "Fungal infections",
            "Neuroprotective applications"
        ],
        "subjective_effects": [
            "Increased alertness",
            "Focus enhancement",
            "Respiratory support",
            "Mental clarity"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Linalool": {
        "chemical_class": "Monoterpene alcohol",
        "molecular_formula": "C₁₀H₁₈O",
        "molar_mass": "154.25",
        "boiling_point": "198 °C (388 °F)",
        "pharmacology": "Sedative and anxiolytic monoterpene alcohol. Modulates GABA receptors and exhibits anticonvulsant properties. Anti-inflammatory through inhibition of NF-κB pathway and antioxidant activity.",
        "therapeutic_indications": [
            "Anxiety disorders",
            "Epilepsy",
            "Depression",
            "Pain management",
            "Inflammatory conditions",
            "Neurodegenerative diseases"
        ],
        "subjective_effects": [
            "Calming effect",
            "Stress relief",
            "Relaxation promotion",
            "Sleep enhancement"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "beta-Caryophyllene": {
        "chemical_class": "Sesquiterpene",
        "molecular_formula": "C₁₅H₂₄",
        "molar_mass": "204.35",
        "boiling_point": "130 °C (266 °F) at 4 mmHg",
        "pharmacology": "Selective agonist at CB2 receptors. Exhibits anti-inflammatory properties through inhibition of pro-inflammatory cytokines. Gastroprotective and neuroprotective effects through multiple pathways.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Pain management",
            "Anxiety disorders",
            "Gastric ulcer protection",
            "Cancer research",
            "Neurodegenerative diseases"
        ],
        "subjective_effects": [
            "Relaxation promotion",
            "Pain relief",
            "Mood enhancement",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "alpha-Caryophyllene": {
        "chemical_class": "Sesquiterpene",
        "molecular_formula": "C₁₅H₂₄",
        "molar_mass": "204.35",
        "boiling_point": "130 °C (266 °F) at 4 mmHg",
        "pharmacology": "Isomer of beta-caryophyllene with similar pharmacological properties. Selective CB2 receptor agonist with anti-inflammatory and gastroprotective effects.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Pain management",
            "Anxiety disorders",
            "Gastric ulcer protection",
            "Cancer research",
            "Neurodegenerative diseases"
        ],
        "subjective_effects": [
            "Relaxation promotion",
            "Pain relief",
            "Mood enhancement",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Terpinolene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "219 °C (426 °F)",
        "pharmacology": "Monocyclic monoterpene with antioxidant and sedative properties. Exhibits antifungal and antibacterial activity. Modulates central nervous system through unknown mechanisms.",
        "therapeutic_indications": [
            "Oxidative stress conditions",
            "Fungal infections",
            "Bacterial infections",
            "Sleep disorders",
            "Cancer research",
            "Inflammatory conditions"
        ],
        "subjective_effects": [
            "Relaxation promotion",
            "Sleep enhancement",
            "Mild euphoria",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Camphene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "159 °C (318 °F)",
        "pharmacology": "Bicyclic monoterpene with antioxidant properties. Inhibits lipid synthesis and exhibits cardioprotective effects. Antimicrobial through membrane disruption mechanisms.",
        "therapeutic_indications": [
            "Oxidative stress conditions",
            "Lipid metabolism disorders",
            "Cardiovascular health",
            "Inflammatory conditions",
            "Microbial infections"
        ],
        "subjective_effects": [
            "Mild stimulation",
            "Respiratory support",
            "Energy enhancement"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "alpha-Phellandrene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "166 °C (331 °F)",
        "pharmacology": "Monocyclic monoterpene with antioxidant and anti-inflammatory properties. Exhibits antimicrobial activity and gastroprotective effects. Modulates cellular signaling pathways.",
        "therapeutic_indications": [
            "Oxidative stress conditions",
            "Inflammatory disorders",
            "Microbial infections",
            "Cancer research",
            "Gastric protection"
        ],
        "subjective_effects": [
            "Mental clarity",
            "Mild energy boost",
            "Enhanced focus"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "beta-Phellandrene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "170 °C (338 °F)",
        "pharmacology": "Isomer of alpha-phellandrene with similar properties. Antioxidant and anti-inflammatory agent. Exhibits antimicrobial activity and cellular protective effects.",
        "therapeutic_indications": [
            "Oxidative stress conditions",
            "Inflammatory disorders",
            "Microbial infections",
            "Cancer research",
            "Gastric protection"
        ],
        "subjective_effects": [
            "Mental clarity",
            "Mild energy boost",
            "Enhanced focus"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "alpha-Terpinene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "186 °C (367 °F)",
        "pharmacology": "Monocyclic monoterpene with antioxidant properties. Exhibits antimicrobial and anti-inflammatory effects. Hepatoprotective through modulation of detoxification enzymes.",
        "therapeutic_indications": [
            "Oxidative stress conditions",
            "Microbial infections",
            "Inflammatory disorders",
            "Cancer research",
            "Liver protection"
        ],
        "subjective_effects": [
            "Mood enhancement",
            "Energy boost",
            "Mental clarity"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "gamma-Terpinene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "182 °C (359 °F)",
        "pharmacology": "Isomer of alpha-terpinene with similar properties. Antioxidant and antimicrobial agent. Anti-inflammatory through inhibition of pro-inflammatory mediators.",
        "therapeutic_indications": [
            "Oxidative stress conditions",
            "Microbial infections",
            "Inflammatory disorders",
            "Cancer research",
            "Liver protection"
        ],
        "subjective_effects": [
            "Mood enhancement",
            "Energy boost",
            "Mental clarity"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "alpha-Terpineol": {
        "chemical_class": "Monoterpene alcohol",
        "molecular_formula": "C₁₀H₁₈O",
        "molar_mass": "154.25",
        "boiling_point": "219 °C (426 °F)",
        "pharmacology": "Sedative monoterpene alcohol with antioxidant properties. Anti-inflammatory through inhibition of NF-κB pathway. Exhibits antimicrobial activity against various pathogens.",
        "therapeutic_indications": [
            "Oxidative stress conditions",
            "Inflammatory disorders",
            "Sleep disorders",
            "Microbial infections",
            "Cancer research"
        ],
        "subjective_effects": [
            "Relaxation promotion",
            "Sleep enhancement",
            "Pain relief",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Caryophyllene-Oxide": {
        "chemical_class": "Sesquiterpene oxide",
        "molecular_formula": "C₁₅H₂₄O",
        "molar_mass": "220.35",
        "boiling_point": "Not established",
        "pharmacology": "Oxidized form of caryophyllene with enhanced biological activity. Anti-inflammatory and antimicrobial properties. Exhibits neuroprotective effects and cellular protective mechanisms.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Microbial infections",
            "Fungal infections",
            "Cancer research",
            "Neurodegenerative diseases"
        ],
        "subjective_effects": [
            "Mild relaxation",
            "Skin soothing",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Geraniol": {
        "chemical_class": "Monoterpene alcohol",
        "molecular_formula": "C₁₀H₁₈O",
        "molar_mass": "154.25",
        "boiling_point": "230 °C (446 °F)",
        "pharmacology": "Monoterpene alcohol with antioxidant properties. Neuroprotective through anti-apoptotic mechanisms. Exhibits antimicrobial activity and anti-inflammatory effects.",
        "therapeutic_indications": [
            "Oxidative stress conditions",
            "Inflammatory disorders",
            "Neurodegenerative diseases",
            "Microbial infections",
            "Cancer research"
        ],
        "subjective_effects": [
            "Relaxation promotion",
            "Skin soothing",
            "Anti-aging effects",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Citronellol": {
        "chemical_class": "Monoterpene alcohol",
        "molecular_formula": "C₁₀H₂₀O",
        "molar_mass": "156.26",
        "boiling_point": "208 °C (406 °F)",
        "pharmacology": "Isomer of geraniol with similar properties. Antioxidant and anti-inflammatory agent. Exhibits neuroprotective and antimicrobial properties through multiple mechanisms.",
        "therapeutic_indications": [
            "Oxidative stress conditions",
            "Inflammatory disorders",
            "Microbial infections",
            "Cancer research",
            "Neurodegenerative diseases"
        ],
        "subjective_effects": [
            "Relaxation promotion",
            "Skin soothing",
            "Anti-aging effects",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "L-Menthol": {
        "chemical_class": "Monoterpene alcohol",
        "molecular_formula": "C₁₀H₂₀O",
        "molar_mass": "156.26",
        "boiling_point": "216 °C (421 °F)",
        "pharmacology": "Cyclic monoterpene alcohol with analgesic properties. Activates TRPM8 receptors producing cooling sensation. Anti-inflammatory and respiratory support through bronchodilation.",
        "therapeutic_indications": [
            "Pain management",
            "Inflammatory conditions",
            "Cooling applications",
            "Respiratory support",
            "Microbial infections"
        ],
        "subjective_effects": [
            "Cooling sensation",
            "Pain relief",
            "Respiratory support",
            "Mental clarity"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "alpha-Bisabolol": {
        "chemical_class": "Sesquiterpene alcohol",
        "molecular_formula": "C₁₅H₂₆O",
        "molar_mass": "222.36",
        "boiling_point": "155 °C (311 °F) at 2 mmHg",
        "pharmacology": "Sesquiterpene alcohol with anti-inflammatory properties. Promotes wound healing and exhibits antimicrobial activity. Neuroprotective through anti-apoptotic mechanisms.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Microbial infections",
            "Wound healing",
            "Cancer research",
            "Neurodegenerative diseases"
        ],
        "subjective_effects": [
            "Skin soothing",
            "Relaxation promotion",
            "Anti-aging effects",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Nerol": {
        "chemical_class": "Monoterpene alcohol",
        "molecular_formula": "C₁₀H₁₈O",
        "molar_mass": "154.25",
        "boiling_point": "224 °C (435 °F)",
        "pharmacology": "Isomer of geraniol with similar properties. Antioxidant and anti-inflammatory agent. Exhibits neuroprotective and antimicrobial properties through cellular mechanisms.",
        "therapeutic_indications": [
            "Oxidative stress conditions",
            "Inflammatory disorders",
            "Microbial infections",
            "Cancer research",
            "Neurodegenerative diseases"
        ],
        "subjective_effects": [
            "Relaxation promotion",
            "Skin soothing",
            "Anti-aging effects",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Sabinene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "167 °C (333 °F)",
        "pharmacology": "Bicyclic monoterpene with anti-inflammatory properties. Exhibits antioxidant and hepatoprotective effects. Antimicrobial through membrane disruption mechanisms.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Oxidative stress conditions",
            "Liver protection",
            "Microbial infections",
            "Cancer research"
        ],
        "subjective_effects": [
            "Digestive support",
            "Respiratory support",
            "Grounding effect"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Delta-3-Carene": {
        "chemical_class": "Monoterpene",
        "molecular_formula": "C₁₀H₁₆",
        "molar_mass": "136.23",
        "boiling_point": "170 °C (338 °F)",
        "pharmacology": "Bicyclic monoterpene with anti-inflammatory properties. Promotes bone healing and exhibits diuretic effects. Antioxidant through free radical scavenging.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Bone fracture healing",
            "Fluid retention",
            "Oxidative stress conditions",
            "Microbial infections"
        ],
        "subjective_effects": [
            "Mental clarity",
            "Bone health support",
            "Energy boost"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "d-Camphor": {
        "chemical_class": "Monoterpene ketone",
        "molecular_formula": "C₁₀H₁₆O",
        "molar_mass": "152.23",
        "boiling_point": "204 °C (399 °F)",
        "pharmacology": "Cyclic monoterpene ketone with analgesic properties. Anti-inflammatory and respiratory support through bronchodilation. Antimicrobial through membrane disruption mechanisms.",
        "therapeutic_indications": [
            "Pain management",
            "Inflammatory conditions",
            "Respiratory support",
            "Microbial infections",
            "Fungal infections"
        ],
        "subjective_effects": [
            "Cooling sensation",
            "Respiratory support",
            "Pain relief",
            "Mental clarity"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Fenchyl Alcohol": {
        "chemical_class": "Monoterpene alcohol",
        "molecular_formula": "C₁₀H₁₈O",
        "molar_mass": "154.25",
        "boiling_point": "210 °C (410 °F)",
        "pharmacology": "Bicyclic monoterpene alcohol with anti-inflammatory properties. Exhibits antimicrobial and antioxidant activity. Neuroprotective through anti-apoptotic mechanisms.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Microbial infections",
            "Oxidative stress conditions",
            "Neurodegenerative diseases",
            "Cancer research"
        ],
        "subjective_effects": [
            "Relaxation promotion",
            "Skin soothing",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Guaiene": {
        "chemical_class": "Sesquiterpene",
        "molecular_formula": "C₁₅H₂₄",
        "molar_mass": "204.35",
        "boiling_point": "Not established",
        "pharmacology": "Sesquiterpene with anti-inflammatory properties. Exhibits antimicrobial and antioxidant activity. Neuroprotective through cellular protective mechanisms.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Microbial infections",
            "Oxidative stress conditions",
            "Cancer research",
            "Neurodegenerative diseases"
        ],
        "subjective_effects": [
            "Relaxation promotion",
            "Skin soothing",
            "Grounding effect"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Isoborneol": {
        "chemical_class": "Monoterpene alcohol",
        "molecular_formula": "C₁₀H₁₈O",
        "molar_mass": "154.25",
        "boiling_point": "212 °C (414 °F)",
        "pharmacology": "Bicyclic monoterpene alcohol with anti-inflammatory properties. Neuroprotective and analgesic effects. Exhibits antioxidant activity through free radical scavenging.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Neurodegenerative diseases",
            "Pain management",
            "Oxidative stress conditions",
            "Microbial infections"
        ],
        "subjective_effects": [
            "Relaxation promotion",
            "Pain relief",
            "Mental clarity",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Cedrene": {
        "chemical_class": "Sesquiterpene",
        "molecular_formula": "C₁₅H₂₄",
        "molar_mass": "204.35",
        "boiling_point": "Not established",
        "pharmacology": "Sesquiterpene with anti-inflammatory properties. Exhibits antimicrobial and antioxidant activity. Neuroprotective through cellular protective mechanisms.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Microbial infections",
            "Oxidative stress conditions",
            "Cancer research",
            "Neurodegenerative diseases"
        ],
        "subjective_effects": [
            "Grounding effect",
            "Relaxation promotion",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Farnesene": {
        "chemical_class": "Sesquiterpene",
        "molecular_formula": "C₁₅H₂₄",
        "molar_mass": "204.35",
        "boiling_point": "120 °C (248 °F) at 1 mmHg",
        "pharmacology": "Sesquiterpene with anti-inflammatory properties. Exhibits antimicrobial and antioxidant activity. Skin protective through cellular mechanisms.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Microbial infections",
            "Oxidative stress conditions",
            "Cancer research",
            "Skin protection"
        ],
        "subjective_effects": [
            "Skin soothing",
            "Anti-aging effects",
            "Stress reduction"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Citral": {
        "chemical_class": "Monoterpene aldehyde",
        "molecular_formula": "C₁₀H₁₆O",
        "molar_mass": "152.23",
        "boiling_point": "229 °C (444 °F)",
        "pharmacology": "Monoterpene aldehyde with antimicrobial properties. Exhibits antioxidant and anxiolytic effects. Anti-inflammatory through inhibition of pro-inflammatory mediators.",
        "therapeutic_indications": [
            "Microbial infections",
            "Oxidative stress conditions",
            "Anxiety disorders",
            "Cancer research",
            "Inflammatory conditions"
        ],
        "subjective_effects": [
            "Uplifted mood",
            "Stress relief",
            "Mental clarity"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    },
    "Valencene": {
        "chemical_class": "Sesquiterpene",
        "molecular_formula": "C₁₅H₂₄",
        "molar_mass": "204.35",
        "boiling_point": "130 °C (266 °F) at 1 mmHg",
        "pharmacology": "Sesquiterpene with anti-inflammatory properties. Exhibits antimicrobial and antioxidant activity. Hepatoprotective through modulation of detoxification enzymes.",
        "therapeutic_indications": [
            "Inflammatory disorders",
            "Microbial infections",
            "Oxidative stress conditions",
            "Cancer research",
            "Liver protection"
        ],
        "subjective_effects": [
            "Uplifted mood",
            "Stress relief",
            "Energy boost"
        ],
        "sources": [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3112269/",
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6826735/"
        ]
    }
}

# Terpene search database with keywords
TERPENE_SEARCH_DATABASE = {
    "beta-Myrcene": {
        "medical_keywords": [
            "anti-inflammatory",
            "analgesic",
            "sedative",
            "pain relief",
            "sleep aid",
            "muscle relaxation",
            "antioxidant"
        ],
        "recreational_keywords": [
            "relaxation",
            "sedation",
            "pain relief",
            "enhanced THC effects"
        ]
    },
    "d-Limonene": {
        "medical_keywords": [
            "anxiolytic",
            "antidepressant",
            "antifungal",
            "acid reflux",
            "immune support",
            "cancer research",
            "gastroprotective"
        ],
        "recreational_keywords": [
            "uplifting mood",
            "stress relief",
            "mental clarity",
            "enhanced focus"
        ]
    },
    "alpha-Pinene": {
        "medical_keywords": [
            "bronchodilator",
            "anti-inflammatory",
            "memory enhancement",
            "antibacterial",
            "antifungal",
            "respiratory support"
        ],
        "recreational_keywords": [
            "alertness",
            "focus enhancement",
            "mental clarity",
            "respiratory support"
        ]
    },
    "beta-Pinene": {
        "medical_keywords": [
            "bronchodilator",
            "anti-inflammatory",
            "memory enhancement",
            "antibacterial",
            "antifungal",
            "respiratory support"
        ],
        "recreational_keywords": [
            "alertness",
            "focus enhancement",
            "mental clarity",
            "respiratory support"
        ]
    },
    "Linalool": {
        "medical_keywords": [
            "anxiolytic",
            "anticonvulsant",
            "antidepressant",
            "analgesic",
            "anti-inflammatory",
            "sedative",
            "neuroprotective"
        ],
        "recreational_keywords": [
            "calming effect",
            "stress relief",
            "relaxation",
            "sleep enhancement"
        ]
    },
    "beta-Caryophyllene": {
        "medical_keywords": [
            "anti-inflammatory",
            "analgesic",
            "anxiolytic",
            "gastroprotective",
            "neuroprotective",
            "anticancer"
        ],
        "recreational_keywords": [
            "relaxation",
            "pain relief",
            "mood enhancement",
            "stress reduction"
        ]
    },
    "alpha-Caryophyllene": {
        "medical_keywords": [
            "anti-inflammatory",
            "analgesic",
            "anxiolytic",
            "gastroprotective",
            "neuroprotective",
            "anticancer"
        ],
        "recreational_keywords": [
            "relaxation",
            "pain relief",
            "mood enhancement",
            "stress reduction"
        ]
    },
    "Terpinolene": {
        "medical_keywords": [
            "antioxidant",
            "antifungal",
            "antibacterial",
            "sedative",
            "anticancer",
            "sleep aid"
        ],
        "recreational_keywords": [
            "relaxation",
            "sleep enhancement",
            "mild euphoria",
            "stress reduction"
        ]
    },
    "Camphene": {
        "medical_keywords": [
            "antioxidant",
            "lipid synthesis inhibitor",
            "cardioprotective",
            "anti-inflammatory",
            "antimicrobial"
        ],
        "recreational_keywords": [
            "mild stimulation",
            "respiratory support",
            "energy enhancement"
        ]
    },
    "alpha-Phellandrene": {
        "medical_keywords": [
            "antioxidant",
            "anti-inflammatory",
            "antimicrobial",
            "anticancer",
            "gastroprotective"
        ],
        "recreational_keywords": [
            "mental clarity",
            "mild energy boost",
            "enhanced focus"
        ]
    },
    "beta-Phellandrene": {
        "medical_keywords": [
            "antioxidant",
            "anti-inflammatory",
            "antimicrobial",
            "anticancer",
            "gastroprotective"
        ],
        "recreational_keywords": [
            "mental clarity",
            "mild energy boost",
            "enhanced focus"
        ]
    },
    "alpha-Terpinene": {
        "medical_keywords": [
            "antioxidant",
            "antimicrobial",
            "anti-inflammatory",
            "anticancer",
            "hepatoprotective"
        ],
        "recreational_keywords": [
            "mood enhancement",
            "energy boost",
            "mental clarity"
        ]
    },
    "gamma-Terpinene": {
        "medical_keywords": [
            "antioxidant",
            "antimicrobial",
            "anti-inflammatory",
            "anticancer",
            "hepatoprotective"
        ],
        "recreational_keywords": [
            "mood enhancement",
            "energy boost",
            "mental clarity"
        ]
    },
    "alpha-Terpineol": {
        "medical_keywords": [
            "antioxidant",
            "anti-inflammatory",
            "sedative",
            "antimicrobial",
            "anticancer"
        ],
        "recreational_keywords": [
            "relaxation",
            "sleep enhancement",
            "pain relief",
            "stress reduction"
        ]
    },
    "Caryophyllene-Oxide": {
        "medical_keywords": [
            "anti-inflammatory",
            "antimicrobial",
            "antifungal",
            "neuroprotective",
            "anticancer"
        ],
        "recreational_keywords": [
            "mild relaxation",
            "skin soothing",
            "stress reduction"
        ]
    },
    "Geraniol": {
        "medical_keywords": [
            "antioxidant",
            "anti-inflammatory",
            "neuroprotective",
            "antimicrobial",
            "anticancer"
        ],
        "recreational_keywords": [
            "relaxation",
            "skin soothing",
            "anti-aging",
            "stress reduction"
        ]
    },
    "Citronellol": {
        "medical_keywords": [
            "antioxidant",
            "anti-inflammatory",
            "antimicrobial",
            "neuroprotective",
            "anticancer"
        ],
        "recreational_keywords": [
            "relaxation",
            "skin soothing",
            "anti-aging",
            "stress reduction"
        ]
    },
    "L-Menthol": {
        "medical_keywords": [
            "analgesic",
            "anti-inflammatory",
            "cooling agent",
            "respiratory support",
            "antimicrobial"
        ],
        "recreational_keywords": [
            "cooling sensation",
            "pain relief",
            "respiratory support",
            "mental clarity"
        ]
    },
    "alpha-Bisabolol": {
        "medical_keywords": [
            "anti-inflammatory",
            "antimicrobial",
            "wound healing",
            "neuroprotective",
            "anticancer"
        ],
        "recreational_keywords": [
            "skin soothing",
            "relaxation",
            "anti-aging",
            "stress reduction"
        ]
    },
    "Nerol": {
        "medical_keywords": [
            "antioxidant",
            "anti-inflammatory",
            "antimicrobial",
            "neuroprotective",
            "anticancer"
        ],
        "recreational_keywords": [
            "relaxation",
            "skin soothing",
            "anti-aging",
            "stress reduction"
        ]
    },
    "Sabinene": {
        "medical_keywords": [
            "anti-inflammatory",
            "antioxidant",
            "hepatoprotective",
            "antimicrobial",
            "anticancer"
        ],
        "recreational_keywords": [
            "digestive support",
            "respiratory support",
            "grounding effect"
        ]
    },
    "Delta-3-Carene": {
        "medical_keywords": [
            "anti-inflammatory",
            "bone healing",
            "diuretic",
            "antioxidant",
            "antimicrobial"
        ],
        "recreational_keywords": [
            "mental clarity",
            "bone health support",
            "energy boost"
        ]
    },
    "d-Camphor": {
        "medical_keywords": [
            "analgesic",
            "anti-inflammatory",
            "respiratory support",
            "antimicrobial",
            "antifungal"
        ],
        "recreational_keywords": [
            "cooling sensation",
            "respiratory support",
            "pain relief",
            "mental clarity"
        ]
    },
    "Fenchyl Alcohol": {
        "medical_keywords": [
            "anti-inflammatory",
            "antimicrobial",
            "antioxidant",
            "neuroprotective",
            "anticancer"
        ],
        "recreational_keywords": [
            "relaxation",
            "skin soothing",
            "stress reduction"
        ]
    },
    "Guaiene": {
        "medical_keywords": [
            "anti-inflammatory",
            "antimicrobial",
            "antioxidant",
            "neuroprotective",
            "anticancer"
        ],
        "recreational_keywords": [
            "relaxation",
            "skin soothing",
            "grounding effect"
        ]
    },
    "Isoborneol": {
        "medical_keywords": [
            "anti-inflammatory",
            "neuroprotective",
            "analgesic",
            "antioxidant",
            "antimicrobial"
        ],
        "recreational_keywords": [
            "relaxation",
            "pain relief",
            "mental clarity",
            "stress reduction"
        ]
    },
    "Cedrene": {
        "medical_keywords": [
            "anti-inflammatory",
            "antimicrobial",
            "antioxidant",
            "neuroprotective",
            "anticancer"
        ],
        "recreational_keywords": [
            "grounding effect",
            "relaxation",
            "stress reduction"
        ]
    },
    "Farnesene": {
        "medical_keywords": [
            "anti-inflammatory",
            "antimicrobial",
            "antioxidant",
            "skin protection",
            "anticancer"
        ],
        "recreational_keywords": [
            "skin soothing",
            "anti-aging",
            "stress reduction"
        ]
    },
    "Citral": {
        "medical_keywords": [
            "antimicrobial",
            "antioxidant",
            "anxiolytic",
            "anticancer",
            "anti-inflammatory"
        ],
        "recreational_keywords": [
            "uplifted mood",
            "stress relief",
            "mental clarity"
        ]
    },
    "Valencene": {
        "medical_keywords": [
            "anti-inflammatory",
            "antimicrobial",
            "antioxidant",
            "hepatoprotective",
            "anticancer"
        ],
        "recreational_keywords": [
            "uplifted mood",
            "stress relief",
            "energy boost"
        ]
    }
}

# Example mixes
EXAMPLE_MIXES = [
    # Medical mixes
    {
        "name": "Chronic Pain Relief",
        "type": "medical",
        "target": "Pain Management",
        "description": "A balanced blend targeting chronic pain with anti-inflammatory properties.",
        "mix": {
            "cannabinoid-THC": 10,
            "cannabinoid-CBD": 15,
            "cannabinoid-CBG": 5,
            "terpene-beta-Myrcene": 8,
            "terpene-beta-Caryophyllene": 6,
            "terpene-Linalool": 4,
            "terpene-alpha-Pinene": 3
        }
    },
    {
        "name": "Sleep Aid",
        "type": "medical",
        "target": "Insomnia",
        "description": "A sedating blend designed to promote deep, restful sleep.",
        "mix": {
            "cannabinoid-CBN": 12,
            "cannabinoid-THC": 5,
            "cannabinoid-CBD": 10,
            "terpene-beta-Myrcene": 10,
            "terpene-Linalool": 8,
            "terpene-Terpinolene": 5,
            "terpene-alpha-Terpineol": 4
        }
    },
    {
        "name": "Anxiety Reduction",
        "type": "medical",
        "target": "Generalized Anxiety",
        "description": "A calming blend focused on reducing anxiety and promoting relaxation without sedation.",
        "mix": {
            "cannabinoid-CBD": 20,
            "cannabinoid-CBG": 8,
            "cannabinoid-THC": 2,
            "terpene-Linalool": 10,
            "terpene-beta-Caryophyllene": 8,
            "terpene-d-Limonene": 6,
            "terpene-alpha-Pinene": 4
        }
    },
    {
        "name": "Neuroprotective Support",
        "type": "medical",
        "target": "Neurodegenerative Conditions",
        "description": "A blend designed to support brain health and protect against neurodegeneration.",
        "mix": {
            "cannabinoid-CBD": 15,
            "cannabinoid-CBG": 12,
            "cannabinoid-THC": 3,
            "terpene-beta-Caryophyllene": 10,
            "terpene-alpha-Pinene": 8,
            "terpene-Linalool": 6,
            "terpene-Geraniol": 5
        }
    },
    {
        "name": "Anti-inflammatory",
        "type": "medical",
        "target": "Inflammatory Conditions",
        "description": "A potent anti-inflammatory blend targeting conditions like arthritis and IBD.",
        "mix": {
            "cannabinoid-CBD": 18,
            "cannabinoid-CBG": 10,
            "cannabinoid-THC": 4,
            "terpene-beta-Caryophyllene": 12,
            "terpene-beta-Myrcene": 10,
            "terpene-alpha-Pinene": 6,
            "terpene-Caryophyllene-Oxide": 5
        }
    },
    # Recreational mixes
    {
        "name": "Euphoric Bliss",
        "type": "recreational",
        "target": "Euphoria & Happiness",
        "description": "A uplifting blend designed to promote feelings of euphoria and well-being.",
        "mix": {
            "cannabinoid-THC": 15,
            "cannabinoid-CBD": 5,
            "terpene-d-Limonene": 12,
            "terpene-beta-Myrcene": 8,
            "terpene-Citral": 6,
            "terpene-Valencene": 5,
            "terpene-Terpinolene": 4
        }
    },
    {
        "name": "Creative Focus",
        "type": "recreational",
        "target": "Enhanced Creativity",
        "description": "A clarity-enhancing blend designed to boost creativity and focus.",
        "mix": {
            "cannabinoid-THC": 8,
            "cannabinoid-CBD": 10,
            "cannabinoid-CBG": 6,
            "terpene-alpha-Pinene": 12,
            "terpene-beta-Pinene": 10,
            "terpene-d-Limonene": 8,
            "terpene-Citronellol": 5
        }
    },
    {
        "name": "Relaxation Station",
        "type": "recreational",
        "target": "Deep Relaxation",
        "description": "A calming blend perfect for unwinding after a long day.",
        "mix": {
            "cannabinoid-THC": 10,
            "cannabinoid-CBD": 12,
            "cannabinoid-CBN": 5,
            "terpene-Linalool": 12,
            "terpene-beta-Myrcene": 10,
            "terpene-alpha-Terpineol": 6,
            "terpene-Geraniol": 5
        }
    },
    {
        "name": "Sensory Enhancer",
        "type": "recreational",
        "target": "Enhanced Sensory Perception",
        "description": "A blend designed to enhance sensory experiences and perception.",
        "mix": {
            "cannabinoid-THC": 12,
            "cannabinoid-CBD": 6,
            "terpene-d-Limonene": 10,
            "terpene-Terpinolene": 8,
            "terpene-beta-Caryophyllene": 6,
            "terpene-Citral": 5,
            "terpene-Fenchyl Alcohol": 4
        }
    },
    {
        "name": "Energy Boost",
        "type": "recreational",
        "target": "Increased Energy",
        "description": "An invigorating blend designed to boost energy and alertness.",
        "mix": {
            "cannabinoid-THC": 6,
            "cannabinoid-CBD": 8,
            "cannabinoid-CBG": 10,
            "terpene-alpha-Pinene": 12,
            "terpene-beta-Pinene": 10,
            "terpene-d-Limonene": 8,
            "terpene-Delta-3-Carene": 6
        }
    }
]

# Dosage guide data
DOSAGE_GUIDE = {
    "cannabinoids": {
        "THC": {
            "description": "Primary psychoactive cannabinoid responsible for the 'high' associated with cannabis. Also has analgesic, anti-inflammatory, and appetite-stimulating properties.",
            "low_dose": "2.5-5 mg",
            "medium_dose": "5-15 mg",
            "high_dose": "15-50 mg"
        },
        "CBD": {
            "description": "Non-psychoactive cannabinoid with anxiolytic, anti-inflammatory, and neuroprotective properties. Often used to counteract THC's psychoactive effects.",
            "low_dose": "5-10 mg",
            "medium_dose": "10-25 mg",
            "high_dose": "25-100 mg"
        },
        "CBG": {
            "description": "Non-psychoactive cannabinoid with anti-inflammatory, neuroprotective, and antibacterial properties. Known as the 'mother of all cannabinoids' as it's a precursor to THC and CBD.",
            "low_dose": "2-5 mg",
            "medium_dose": "5-15 mg",
            "high_dose": "15-50 mg"
        },
        "CBN": {
            "description": "Mildly psychoactive cannabinoid with sedative properties. Formed when THC degrades. Known for its potential to aid sleep and reduce inflammation.",
            "low_dose": "2-5 mg",
            "medium_dose": "5-15 mg",
            "high_dose": "15-30 mg"
        }
    },
    "terpenes": {
        "alpha-Bisabolol": {
            "description": "Sesquiterpene alcohol with anti-inflammatory, antimicrobial, and skin-healing properties. Found in chamomile and some cannabis varieties.",
            "low_dose": "1-5 mg",
            "medium_dose": "5-15 mg",
            "high_dose": "15-30 mg"
        },
        "alpha-Caryophyllene": {
            "description": "Sesquiterpene found in black pepper, cloves, and cannabis. Binds to CB2 receptors and has anti-inflammatory properties.",
            "low_dose": "2-5 mg",
            "medium_dose": "5-15 mg",
            "high_dose": "15-30 mg"
        },
        "alpha-Phellandrene": {
            "description": "Monoterpene with antimicrobial and anti-inflammatory properties. Found in eucalyptus and peppermint oils.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "alpha-Pinene": {
            "description": "Monoterpene found in pine trees and cannabis. Bronchodilator that may counteract THC's memory-impairing effects.",
            "low_dose": "2-5 mg",
            "medium_dose": "5-15 mg",
            "high_dose": "15-30 mg"
        },
        "alpha-Terpinene": {
            "description": "Monoterpene with antioxidant and antimicrobial properties. Found in citrus peels and some cannabis varieties.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "alpha-Terpineol": {
            "description": "Monoterpene alcohol with sedative and antioxidant properties. Often found in lilacs and some cannabis varieties.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "beta-Caryophyllene": {
            "description": "Sesquiterpene found in black pepper, cloves, and cannabis. Binds to CB2 receptors and has anti-inflammatory properties.",
            "low_dose": "2-5 mg",
            "medium_dose": "5-15 mg",
            "high_dose": "15-30 mg"
        },
        "beta-Myrcene": {
            "description": "Monoterpene with sedative, anti-inflammatory, and analgesic properties. Found in mangoes, hops, and some cannabis varieties.",
            "low_dose": "2-5 mg",
            "medium_dose": "5-15 mg",
            "high_dose": "15-30 mg"
        },
        "beta-Phellandrene": {
            "description": "Monoterpene with antimicrobial and anti-inflammatory properties. Found in various essential oils.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "beta-Pinene": {
            "description": "Monoterpene found in pine trees and cannabis. Bronchodilator that may counteract THC's memory-impairing effects.",
            "low_dose": "2-5 mg",
            "medium_dose": "5-15 mg",
            "high_dose": "15-30 mg"
        },
        "Camphene": {
            "description": "Monoterpene with antioxidant and lipid-lowering properties. Found in camphor oil and some cannabis varieties.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Caryophyllene-Oxide": {
            "description": "Oxidized form of caryophyllene with anti-inflammatory and antimicrobial properties.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Cedrene": {
            "description": "Sesquiterpene with anti-inflammatory and antimicrobial properties. Found in cedarwood oil.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Citral": {
            "description": "Monoterpene aldehyde with antimicrobial and anxiolytic properties. Found in lemongrass and citrus oils.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Citronellol": {
            "description": "Monoterpene alcohol with antimicrobial and anti-inflammatory properties. Found in citronella oil.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "d-Camphor": {
            "description": "Monoterpene ketone with analgesic and anti-inflammatory properties. Found in camphor oil.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "d-Limonene": {
            "description": "Monoterpene with anxiolytic and gastroprotective properties. Found in citrus peels and some cannabis varieties.",
            "low_dose": "5-10 mg",
            "medium_dose": "10-25 mg",
            "high_dose": "25-50 mg"
        },
        "Delta-3-Carene": {
            "description": "Monoterpene with anti-inflammatory properties. May aid in bone healing and has a diuretic effect.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Farnesene": {
            "description": "Sesquiterpene with anti-inflammatory and antimicrobial properties. Found in various essential oils.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Fenchyl Alcohol": {
            "description": "Monoterpene alcohol with anti-inflammatory and antimicrobial properties. Found in fennel oil.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "gamma-Terpinene": {
            "description": "Monoterpene with antioxidant and antimicrobial properties. Found in various essential oils.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Geraniol": {
            "description": "Monoterpene alcohol with antioxidant and neuroprotective properties. Found in geranium oil.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Guaiene": {
            "description": "Sesquiterpene with anti-inflammatory and antimicrobial properties. Found in guaiac wood oil.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Isoborneol": {
            "description": "Monoterpene alcohol with anti-inflammatory and analgesic properties. Found in various essential oils.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "L-Menthol": {
            "description": "Monoterpene alcohol with analgesic and cooling properties. Found in peppermint oil.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Linalool": {
            "description": "Monoterpene alcohol with anxiolytic and sedative properties. Found in lavender and some cannabis varieties.",
            "low_dose": "2-5 mg",
            "medium_dose": "5-15 mg",
            "high_dose": "15-30 mg"
        },
        "Nerol": {
            "description": "Monoterpene alcohol with antioxidant and anti-inflammatory properties. Found in neroli oil.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Sabinene": {
            "description": "Monoterpene with anti-inflammatory and hepatoprotective properties. Found in black pepper and some cannabis varieties.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        },
        "Terpinolene": {
            "description": "Monoterpene with antioxidant and sedative properties. Found in some cannabis varieties and essential oils.",
            "low_dose": "2-5 mg",
            "medium_dose": "5-15 mg",
            "high_dose": "15-30 mg"
        },
        "Valencene": {
            "description": "Sesquiterpene with anti-inflammatory and hepatoprotective properties. Found in citrus peels.",
            "low_dose": "1-3 mg",
            "medium_dose": "3-10 mg",
            "high_dose": "10-20 mg"
        }
    }
}

def calculate_effects(cannabinoids, terpenes):
    # Determine dominant compounds
    total_cannabinoids = sum(cannabinoids.values())
    total_terpenes = sum(terpenes.values())
    
    dominant_cannabinoid = max(cannabinoids, key=cannabinoids.get) if total_cannabinoids > 0 else None
    dominant_terpene = max(terpenes, key=terpenes.get) if total_terpenes > 0 else None
    
    # Calculate effect intensities (simplified model)
    medical_effects = {}
    recreational_effects = {}
    sources = set()
    
    # Process cannabinoids
    for cannabinoid, amount in cannabinoids.items():
        if amount > 0 and cannabinoid in COMPOUND_DATABASE:
            data = COMPOUND_DATABASE[cannabinoid]
            intensity = min(amount / 50, 1.0)  # Normalize to 0-1 scale
            
            # Add therapeutic indications as medical effects
            for indication in data.get("therapeutic_indications", []):
                medical_effects[indication] = medical_effects.get(indication, 0) + intensity
            
            # Add subjective effects as recreational effects
            for effect in data.get("subjective_effects", []):
                recreational_effects[effect] = recreational_effects.get(effect, 0) + intensity
            
            sources.update(data.get("sources", []))
    
    # Process terpenes
    for terpene, amount in terpenes.items():
        if amount > 0 and terpene in COMPOUND_DATABASE:
            data = COMPOUND_DATABASE[terpene]
            intensity = min(amount / 20, 1.0)  # Normalize to 0-1 scale
            
            # Add therapeutic indications as medical effects
            for indication in data.get("therapeutic_indications", []):
                medical_effects[indication] = medical_effects.get(indication, 0) + intensity
            
            # Add subjective effects as recreational effects
            for effect in data.get("subjective_effects", []):
                recreational_effects[effect] = recreational_effects.get(effect, 0) + intensity
            
            sources.update(data.get("sources", []))
    
    return {
        "dominant_cannabinoid": dominant_cannabinoid,
        "dominant_terpene": dominant_terpene,
        "medical_effects": medical_effects,
        "recreational_effects": recreational_effects,
        "sources": list(sources)
    }

def open_browser():
    """Open the default web browser to the application"""
    global browser_opened
    if not browser_opened:
        webbrowser.open("http://localhost:5000")
        browser_opened = True

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, 
                                compound_database=COMPOUND_DATABASE,
                                example_mixes=EXAMPLE_MIXES,
                                terpene_search_database=TERPENE_SEARCH_DATABASE,
                                dosage_guide=DOSAGE_GUIDE)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    
    # Extract cannabinoid and terpene values
    cannabinoids = {}
    terpenes = {}
    
    for key, value in data.items():
        if key.startswith('cannabinoid-'):
            cannabinoid = key.split('-')[1]
            cannabinoids[cannabinoid] = value
        elif key.startswith('terpene-'):
            terpene = key.split('-')[1]
            terpenes[terpene] = value
    
    # Simulate processing time
    time.sleep(2)
    
    # Calculate effects
    results = calculate_effects(cannabinoids, terpenes)
    
    return jsonify(results)

if __name__ == '__main__':
    print("Starting Cannabis Calculator...")
    
    # Open browser in a separate thread to avoid blocking
    threading.Timer(1.25, open_browser).start()
    
    print("Opening browser to http://localhost:5000")
    app.run(debug=True, use_reloader=False, host='0.0.0.0')