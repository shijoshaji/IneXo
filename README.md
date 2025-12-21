<div align="center">
  <img src="assets/logo-inexo-banner.png" alt="IneX̂ō Banner" width="100%" style="border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);"> 

  <br>

  **Your Balance Keeper for Everyday Money — Powered by IneX̂ō**

  [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
  [![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
  [![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
  [![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com/)
  [![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)<br/>
  [![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
  [![Podman](https://img.shields.io/badge/Podman-892CA0?style=flat&logo=podman&logoColor=white)](https://podman.io/)
  [![Windows](https://img.shields.io/badge/Windows-0078D6?style=flat&logo=windows&logoColor=white)](https://www.microsoft.com/windows/)
  [![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black)](https://www.linux.org/)<br/>
  [![macOS](https://img.shields.io/badge/mac%20os-000000?style=flat&logo=apple&logoColor=white)](https://www.apple.com/macos/)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

  Created by **[Shijo Shaji](https://bio.link/shijoshaji)**  for **IneX̂ō**.
  
  *Made with ❤️ for better financial tracking* 
  <hr>
  <br>
</div>


## ✨ Story Behind “IneX̂ō”
- “In” for Income, “eX̂” for Expense, woven together with the stylized ō symbolizes  operations 
> Tagline: **Track. Save. Thrive.**



## About

**IneX̂ō** (“in-EX-oh” 🔊) is part of the FōX̂iИ Suite (“fox-een” 🔊) — a family of intelligent finance apps ([NAViō](https://github.com/shijoshaji/NAVio), [IneX̂ō](https://github.com/shijoshaji/IneXo), [FiИōra](https://bio.link/shijoshaji)) built to help you track, save, and thrive your financial journey with clarity and confidence.

**IneX̂ō** allows users to securely track income, expenses, investments, debts, credit card usage, and vehicle maintenance costs and more. It features multi-user support, interactive dashboards, and detailed analytics to help you stay on top of your financial health.




## 🚀 Features

- **🔐 Multi-User Authentication**: Secure login system ensuring data isolation between users.
  - **Default Admin user/password**: `shijo`/`admin123`
  - Login and create your admin user/password and then delete the default admin
- **📊 Interactive Dashboard**: Real-time overview of your financial status including Total Income, Expenses, Savings Rate, and Net Savings.
- **📝 Transaction Management**:
  - Add, Edit, and Delete transactions.
  - Support for multiple types: Income, Expense, Investment, Credit Card, Debt, Vehicle, Banking.
- **🏷️ Category Management**: Fully customizable categories for each transaction type.
- **📈 Advanced Analytics**:
  - View data by Current Month, Previous Month, Quarterly, Year-to-Date, or Custom Range.
  - Breakdowns by category (Pie & Bar charts).
  - Monthly Trend analysis.
  - Credit Card spending patterns and limit tracking.
- **🔄 Recurring Items Manager**: Plan your monthly budget by tracking expected income and expenses (Subscriptions, Rent, etc.) for better projections.
- **💱 Currency Support**: Dynamic currency selection (INR, USD, EUR, etc.) with automatic formatting and "Amount in Words" display.
- **💾 Auto-Backup**: Automatic database backup to Git on startup and shutdown.
- **🚗 Vehicle Tracker**: Dedicated module to track fuel, service, and insurance costs separately from general savings.
- **⚖️ Comparisons**: Compare financial performance Month-over-Month or Year-over-Year.

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Framework**: [Streamlit](https://streamlit.io/)
- **Database**: SQLite
- **Data Manipulation**: Pandas
- **Visualization**: Plotly Express & Graph Objects

## 📥 Installation

1.  **Clone the repository** (or download the source code):

    ```bash
    git clone <repository-url>
    cd "inexo"
    ```

2.  **Set up a Virtual Environment** (Optional but recommended):

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ How to Run

### Method 1: Using the Batch Script (Windows) - **Recommended**

Double-click the `localrun\inexo_start.bat` file.

- **Auto-Backup**: This script automatically starts a background backup job (`inexo_auto_backup_db.ps1`) to secure your data.
- **App Launch**: Activates the environment and opens the app in your browser.

### Method 2: Command Line

Open your terminal in the project folder:

```bash
streamlit run app.py
```

## 🔑 Default Credentials

When you first run the application, use the following credentials to log in:

- **Username**: `shijo`
- **Password**: `admin123`

> **Note**: You can change your password in the **Profile** section after logging in. Admin users can also manage other users via the Settings page.

## 📂 Project Structure

- `app.py`: Main UI logic and page routing.
- `database.py`: Database CRUD operations and schema management.
- `finance_utils.py`: Helper functions for currency formatting and "Amount in Words" conversion.
- `finance.db`: Local SQLite database.
- `assets/`: Images and icons (Logo, Favicon).
- `localrun\inexo_start.bat`: Launcher script.
- `localrun\inexo_auto_backup_db.ps1`: PowerShell script for automated git backups.

## 📚 Documentation

Detailed documentation is available in the `Documentation/` folder:

- **[Installation & Usage](Documentation/Installation_Usage.md)**: Setup guide for Windows (Manual/Batch), Docker, Podman, and Troubleshooting.
- **[Database Logic & Sync](Documentation/DB_Synchronization.md)**: Critical info on data persistence and local vs container syncing.
- **[Functional Walkthrough](Documentation/Functional_Walkthrough.md)**: User guide explaining all features and flows.
- **[Technical Walkthrough](Documentation/technical_walkthrough.md)**: Developer guide explaining the architecture, code structure, and logic.

## 🤝 Contribution

Feel free to fork this project and submit pull requests for any enhancements or bug fixes.

**Created by [Shijo Shaji](https://bio.link/shijoshaji) for IneX̂ō.** 

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Streamlit** for the amazing rapid application framework
- **Pandas** for powerful data manipulation
- **Plotly** for beautiful interactive visualizations
- **Python Community** for the endless support and libraries

## 📞 Support

For issues or questions:

- Check `Documentation/Installation_Usage.md`
- Review Troubleshooting in `Documentation/Installation_Usage.md`
- Made with ❤️ for better financial tracking

>#vibeprogrammingwithjo❤️
