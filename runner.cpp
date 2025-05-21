#include <iostream>
#include <fstream>
#include <string>
#include <windows.h>

bool isPythonInstalled() {
    // Check if python command is available
    int result = system("python --version > nul 2>&1");
    return result == 0;
}

bool isPackageInstalled(const std::string& package) {
    std::string cmd = "pip show " + package + " > nul 2>&1";
    int result = system(cmd.c_str());
    return result == 0;
}

bool installPython() {
    if (isPythonInstalled()) {
        std::cout << "Python is already installed. Skipping installation...\n";
        return true;
    }

    std::cout << "Downloading Python installer...\n";
    system("curl https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe -o python_installer.exe");
    
    std::cout << "Installing Python...\n";
    system("python_installer.exe /quiet InstallAllUsers=1 PrependPath=1");
    
    // Clean up installer
    system("del python_installer.exe");
    
    return isPythonInstalled();
}

bool installDependencies() {
    bool allInstalled = true;
    std::string packages[] = {"pandas", "tkcalendar", "matplotlib"};
    
    for (const auto& package : packages) {
        if (!isPackageInstalled(package)) {
            std::cout << "Installing " << package << "...\n";
            std::string cmd = "pip install " + package;
            system(cmd.c_str());
            allInstalled = allInstalled && isPackageInstalled(package);
        } else {
            std::cout << package << " is already installed. Skipping...\n";
        }
    }
    
    return allInstalled;
}

bool createPythonScript() {
    // Check if script already exists
    std::ifstream checkFile("taskmanv1.py");
    if (checkFile.good()) {
        std::cout << "Python script already exists. Skipping creation...\n";
        checkFile.close();
        return true;
    }
    
    std::ofstream outFile("taskmanv1.py");
    if (!outFile) {
        return false;
    }
    
    // Write the Python script content
    outFile << R"(
// ... existing code ...
    )";
    
    outFile.close();
    return true;
}

int main() {
    std::cout << "Finance Tracker Installer\n";
    std::cout << "========================\n\n";
    
    if (!installPython()) {
        std::cout << "Failed to install/verify Python!\n";
        return 1;
    }
    
    if (!installDependencies()) {
        std::cout << "Failed to install/verify dependencies!\n";
        return 1;
    }
    
    std::cout << "Setting up Finance Tracker...\n";
    if (!createPythonScript()) {
        std::cout << "Failed to create Python script!\n";
        return 1;
    }
    
    std::cout << "Starting Finance Tracker...\n";
    // Get the current working directory
    char buffer[MAX_PATH];
    GetCurrentDirectory(MAX_PATH, buffer);
    std::string path(buffer);
    std::string pythonCmd = "python \"" + path + "\\taskmanv1.py\"";
    
    int result = system(pythonCmd.c_str());
    if (result != 0) {
        std::cout << "Failed to start Finance Tracker! Error code: " << result << "\n";
        return 1;
    }
    
    return 0;
}
