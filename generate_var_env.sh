#!/usr/bin/env bash
# File: generate_var_env.sh
# Description: This script generates a .env file from example.env, replacing placeholder values with secure defaults.

set -euo pipefail

# Constants
EXAMPLE_ENV="example.env"
OUTPUT_ENV=".env"

# Function: install_python
# Description: Installs Python 3 and pip on Ubuntu
# Arguments: None
# Returns: None
install_python() {
    echo "Python 3 is not installed. Attempting to install Python 3..."
    if ! command -v sudo &> /dev/null; then
        echo "Error: 'sudo' is required to install Python. Please install sudo or run this script with root privileges." >&2
        exit 1
    fi
    sudo apt update
    sudo apt install -y python3 python3-pip
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
}

# Function: check_and_install_python
# Description: Checks for Python and installs it if not present
# Arguments: None
# Returns: None
check_and_install_python() {
    if ! command -v python3 &> /dev/null; then
        install_python
    fi
    PYTHON_CMD="python3"
    # Install required Python packages
    $PYTHON_CMD -m pip install --user cryptography
}

# Function: replace_value
# Description: Replaces a value in the .env file for a given key
# Arguments:
# $1 (string): The key to replace
# $2 (string): The new value
# Returns: None
replace_value() {
    local key="$1"
    local value="$2"
    sed -i.bak "s|^$key=.*|$key=$value|" "$OUTPUT_ENV" && rm "$OUTPUT_ENV.bak"
}

# Function: generate_openssl_secret
# Description: Generates a secret using openssl
# Arguments: None
# Returns:
# string: The generated secret
generate_openssl_secret() {
    openssl rand -hex 32
}

# Function: generate_python_secret
# Description: Generates a secret using Python
# Arguments: None
# Returns:
# string: The generated secret
generate_python_secret() {
    $PYTHON_CMD -c "import secrets; print(secrets.token_hex(16))"
}

# Function: generate_fernet_key
# Description: Generates a Fernet key using Python
# Arguments: None
# Returns:
# string: The generated Fernet key
generate_fernet_key() {
    $PYTHON_CMD -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
}

# Function: main
# Description: Main function to generate the .env file
# Arguments: None
# Returns: None
main() {
    echo "Generating .env file from $EXAMPLE_ENV"

    # Check and install Python if necessary
    check_and_install_python

    # Copy example.env to .env
    cp "$EXAMPLE_ENV" "$OUTPUT_ENV"

    # Replace values with generated secrets or environment variables
    replace_value "API_SECRET_KEY" "$(generate_openssl_secret)"
    replace_value "AIRFLOW_SECRET_KEY" "$(generate_python_secret)"
    replace_value "AIRFLOW_FERNET_KEY" "$(generate_fernet_key)"
    replace_value "AIRFLOW_UID" "$(id -u)"

    echo ".env file generated successfully"
}

# Run the main function
main

exit 0
