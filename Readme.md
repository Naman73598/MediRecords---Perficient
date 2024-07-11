# MEDIRECORDS: Seamless Care Starts Here
Jira Workflow
![medirecords_2024-07-09_04 25pm](https://github.com/Naman73598/MediRecords-Seamless-Care-Starts-Here/assets/78019442/abdef1cf-b0b3-4c40-b65f-dc5f8af74b91)
 
 
## Team Members
1. Naman Agrahari
2. Athul Robert
3. Thilagavathy Ravi
4. Abhishek Saha
5. Hardik Maheshwari
 
## Abstract
In today's healthcare industry, efficient management of patient and medical data is paramount. Traditional methods are often cumbersome, prompting the need for cost-effective Healthcare Information Management Systems (HIMS). Our project aims to develop a comprehensive HIMS application to streamline data management in healthcare institutions. This system supports patient record management, data visualization, and integrates with external APIs for enhanced functionality.
 
## Functional Requirements Specification
 
### User Management
- **Admin Registration:** Capture essential details securely.
- **Admin Authentication:** Implement secure login functionality.
- **Doctor Data Management:** Assign doctors to patients and fetch doctor details.
 
### Patient Management
- **Patient Registration:** Capture patient information securely.
- **Patient Data Management:** Update and delete patient records securely.
- **Medical Records Management:** Create, modify, and fetch medical records securely.
 
### Data Export
- **Data View:** Secure export functionality for authorized users.
 
### Data Visualization
- **Analytic View:** Visualize patient demographics and medical conditions.
 
### API Consumption
- **Data Integration:** Integrate with external APIs securely.
 
 
## Requirements
- Python 3.7.4 or any higher version
- pandas
- Flask
- flask_mysqldb
- matplotlib
- numpy
- Thunderclient/Postman v11
 
To install these packages, follow these steps:
 
1. Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
 
2. Open a command prompt or terminal.
 
3. Install the required Python packages using pip. Execute the following commands:
 
   ```bash
   pip install pandas
   pip install Flask
   pip install flask-mysqldb
   pip install matplotlib
   pip install numpy
   pip install flask_jwt_extended
 
 
# Application Setup and Instructions
 
## Clone the Repository
Clone this repository to your local system using the following command:
```bash
git clone <repository-url>
```
## Configure Database Connection
Navigate to the DatabaseConnection folder and update the **connection.py** file with your own database credentials.
 
## Update Path in app.py
In the **app.py** file, update the paths for Dataset, Datasetdoctor, and Datasetjson under the **@app.route('/insert')** and **@app.route('/insertdoctor')** sections.
 
## Run the Application
Execute the following command in your terminal to start the application:
```bash
python app.py
```
 
## Initialize Data
Use Thunderclient or Postman to initialize the application data by sending requests in the following order:
 
- Access __http://localhosturl/insertdoctor__ to populate doctor data.
- Access __http://localhosturl/insert__ to populate patient data.
 
 
## Sequence diagram
![Sequence diagram Admin-Patient](https://github.com/Naman73598/MediRecords-Seamless-Care-Starts-Here/assets/78019442/d3953dfa-7c88-44ed-9aed-9b79a255544a)
![Sequence diagram Admin-Doctor](https://github.com/Naman73598/MediRecords-Seamless-Care-Starts-Here/assets/78019442/d6edd5fd-c895-4767-b099-0b2be8995768)
 
## ER diagram
![ER Diagram](https://github.com/Naman73598/MediRecords-Seamless-Care-Starts-Here/assets/126481000/58e2e757-81fc-44b4-b56a-ae00775d7444)
 
 
 
---
 
This project aims to revolutionize healthcare data management by providing a scalable, secure, and user-friendly solution for healthcare providers. For more details, refer to our documentation and codebase.
   