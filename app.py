from openai import OpenAI
import os

# Initialize OpenAI client with your API key
client = OpenAI(api_key="API_KEY")

# Define the system response indicating the task
system_response = (
    "You are the document or datasheet reader and a file creator. "
    "You will analyze the datasheet to identify the register names, addresses of the IPs/protocols, interfaces, "
    "base addresses, and create structures as union members for accessing register bits. "
    "You will generate a C header file for the specified peripheral with macro definitions, function declarations, base addresses, memory mappings, and structures as union members for accessing register bits. "
    "Based on the function declarations, you will also create the corresponding driver code implementations."
)

# Path to the datasheet
datasheet_path = "/mnt/data/LPC2148.pdf"

# List of peripherals
peripherals = ["GPIO", "UART", "SPI", "I2C"]

# Function to ensure directory exists or create it
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Path to the folders
header_folder = "./headers/"
source_folder = "./source/"

# Ensure directories exist
ensure_directory_exists(header_folder)
ensure_directory_exists(source_folder)

# Function to save files in respective folders
def save_files(peripheral, header_content, driver_content):
    # Save header file
    header_filename = f"{header_folder}{peripheral}_Peripheral.h"
    with open(header_filename, "w") as header_file:
        header_file.write(header_content)

    # Save driver file
    driver_filename = f"{source_folder}{peripheral}_Driver.c"
    with open(driver_filename, "w") as driver_file:
        driver_file.write(driver_content)

    print(f"Header file saved as {header_filename}")
    print(f"Driver file saved as {driver_filename}")

# Function to process each peripheral and generate a header file and driver code
def generate_header_and_driver_files(peripheral):
    user_prompt = (
        f"Read the datasheet from {datasheet_path} and generate the header file for the {peripheral} peripheral. "
        "Include macro definitions, function declarations, base addresses, memory mappings, and structures as union members for accessing register bits. "
        "Based on the function declarations, create the corresponding driver code implementations."
    )

    while True:
        # Make a request to the OpenAI API for chat completion
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_response},
                {"role": "user", "content": user_prompt}
            ]
        )

        # Extract the generated response
        generated_response = completion.choices[0].message.content

        # Check if the response contains the desired output
        if "```" in generated_response:
            # Split the response to extract the header and driver file content
            code_blocks = generated_response.split("```")

            # Extract header file content
            header_file_content = code_blocks[1].strip()

            # Remove the 'c' from the first line if present
            if header_file_content.startswith("c\n"):
                header_file_content = header_file_content.replace("c\n", "", 1)

            # Extract driver code content
            driver_file_content = code_blocks[3].strip() if len(code_blocks) > 3 else ""

            # Save files in respective folders
            save_files(peripheral, header_file_content, driver_file_content)
            break
        else:
            print(f"The response for {peripheral} did not contain the expected header and driver file content. Trying again...")

# Iterate through the peripherals and generate header and driver files
for peripheral in peripherals:
    generate_header_and_driver_files(peripheral)
