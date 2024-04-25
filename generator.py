import os
import sys
import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak

# Function to fetch JSON data from the API
def fetch_data(url, headers):
    response = requests.get(url, headers=headers, verify=False)
    data = response.json()
    return data
 
    

def add_title(elements, font_size, title, spaces):
    # Add title
    title_style = ParagraphStyle('TitleStyle', alignment=TA_CENTER, fontSize=font_size, fontName='Helvetica-Bold')
    title = Paragraph(title, title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Add spaces
    style = getSampleStyleSheet()['BodyText']
    for i in range(0, spaces):
        elements.append(Paragraph("\n", style)) 

def add_linebreaks(elements, spaces):
    # Add linebreaks
    style = getSampleStyleSheet()['BodyText']
    for i in range(0, spaces):
        elements.append(Paragraph("\n", style)) 

def generate_pdf(region_list, console_path_url):
    doc = SimpleDocTemplate("cloud_discovery_report.pdf", pagesize=letter)
    elements = []
    add_title(elements, 16, '<h1>Prisma Cloud CWP Protected/Unprotected Assets Report</h1> ', 3)

    # Loop through each AWS region
    for aws_region in region_list:
        # Add title for region
        add_title(elements, 14, f'<h1>Region: {aws_region}</h1> ', 3)

        list_defended_by_region_url = f"{console_path_url}/api/v1/cloud/discovery?limit=5&offset=0&project=Central+Console&region={aws_region}&reverse=true&sort=undefended"
        data1 = fetch_data(list_defended_by_region_url, headers)

        if not data1:
            continue
        print('region', aws_region)
        print('data1', data1)
        # Table 1 with data from the first API endpoint
        table_data1 = [
            [ "Service", "Region", "Defended", "Undefended", "Account", "Total"]
        ]
        for item in data1:
            table_data1.append([
                item["serviceType"],
                item["region"],
                str(item["defended"]),
                str(item["undefended"]),
                item["accountID"],
                str(item["total"])
            ])

        
        # Create Table 1
        table1 = Table(table_data1)
        style1 = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        table1.setStyle(style1)
        elements.append(table1)
        add_linebreaks(elements, 3)
        # elements.append(PageBreak())

        # Loop through data1 to get accountID and serviceType
        for item in data1:
            account_id = item["accountID"]
            service_type = item["serviceType"]
            print('account_id', account_id)
            print('service_type', service_type)
            # Initialize an empty table_data2
            table_data2 = []
            list_defended_by_account_id_url = f"{console_path_url}/api/v1/cloud/discovery/entities?accountIDs={account_id}&limit=8&offset=0&project=Central+Console&region={aws_region}&reverse=false&serviceType={service_type}&sort=defended"

            add_title(elements, 12, f'<h1>{service_type}</h1>', 1)
            if service_type == "aws-ecs":
                # Fetch data from the third URL for the specific accountID and serviceType
                data2 = fetch_data(list_defended_by_account_id_url, headers)
                
                if data2:
                    # print('data2', data2)
                    table_data2.extend([
                        ["Region",  "Name", "Running\nTasks", "Active\nServices", "Nodes", "Account\nID"],
                        *[[
                            item["region"],
                            item["name"],
                            str(item["runningTasksCount"]),
                            str(item["activeServicesCount"]),
                            str(item["nodesCount"]),
                            item["accountID"],
                        ] for item in data2]
                    ])
                    column_widths = [
                        1.2 * inch,   # Region
                        2.0 * inch,  # Name
                        0.6 * inch,  # Running Tasks Count
                        0.6 * inch,  # Active Services Count
                        0.5 * inch,  # Nodes Count
                        1.0 * inch,  # Account ID
                        0.6 * inch   # Service Type
                    ]

            elif service_type == "aws-lambda":
                data2 = fetch_data(list_defended_by_account_id_url, headers)
            
                if data2:
                    # print('data2', data2)
                    table_data2.extend([
                        ["Region",  "Name", "Runtime", "Version", "Account\nID"],
                        *[[
                            item["region"],
                            item["name"],
                            item["runtime"],
                            item["version"],
                            item["accountID"]
                        ] for item in data2]
                    ])
                     # Create Table 2
                    column_widths = [
                        1.2 * inch,   # Region
                        3.6 * inch,  # Name
                        0.8 * inch,  # Runtime
                        0.8 * inch,  # Version
                        1.0 * inch,  # Account ID
                        0.6 * inch   # Service Type
                    ]
            elif service_type == "aws-ecr":
                data2 = fetch_data(list_defended_by_account_id_url, headers)
                
                if data2:
                    table_data2.extend([
                        ["Region", "Registry"],
                        *[[
                            item["region"],
                            item["registry"],
                        ] for item in data2]
                    ])

                    column_widths = [
                        1.2 * inch,   # Region
                        3.6 * inch,  # Registry
                    ]
            elif service_type == "aws-eks":
                data2 = fetch_data(list_defended_by_account_id_url, headers)
                
                if data2:
                    # print('data2', data2)
                    table_data2.extend([
                        [ "Region",  "Name", "Nodes\nCount", "Version", "Account\nID"],
                        *[[
                            item["region"],
                            item["name"],
                            item["nodesCount"],
                            item["version"],
                            item["accountID"]
                        ] for item in data2]
                    ])

                    column_widths = [
                        1.2 * inch,   # Region
                        2.4 * inch,  # Name
                        0.6 * inch,  # Node Count
                        0.8 * inch,  # Version
                        1.0 * inch,  # Account ID
                    ]        
            elif service_type == "aws-ec2":
                    # Fetch data for EC2
                    list_defended_by_account_id_url = f"{console_path_url}/api/v1/cloud/discovery/vms?accountIDs={account_id}&limit=8&offset=0&project=Central+Console&provider=aws&region={aws_region}&reverse=false&sort=hasDefender"
                    ec2_data = fetch_data(list_defended_by_account_id_url, headers)

                    if ec2_data:
                        # print('ec2_data', ec2_data)
                        table_data2.extend([
                            ["Region", "Instance-Id", "Hostname", "Arch", "Account\nID"],
                            *[[
                                item["region"],
                                item["_id"],
                                item["hostname"],
                                item["architecture"],
                                item["accountID"]
                            ] for item in ec2_data]
                        ])
                    column_widths = [
                        1.2 * inch,  #  Region
                        1.4 * inch,   # Instance ID
                        1.6 * inch,  # Hostname
                        0.6 * inch,  # Architecture
                        1.0 * inch,  # Account ID
                    ]
            
            if data2:
                print('data2', data2)
                print('table_data2', table_data2)
                table2 = Table(table_data2, colWidths=column_widths)
                style2 = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black)])
                
                table2.setStyle(style2)
                elements.append(table2)
                add_linebreaks(elements, 3)

        elements.append(PageBreak())

    # Build PDF with all tables
    doc.build(elements)
    print("PDF generated successfully")


def get_access_token(**auth_param):
    
    username = auth_param.get('username', '')
    password = auth_param.get('password', '')
    cwp_console_path = auth_param.get('cwp_console_path', '')

    if not (username and password and cwp_console_path):
        print("Error: Username or password or path to console not found in environment variables.")
        return None

    # Runtime Security -> System -> Utilities -> Path to Console + 'api/v1/authenticate'
    console_auth_url = f'{cwp_console_path}/api/v1/authenticate' 
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json; charset=UTF-8"
    }
    data = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(console_auth_url, json=data, headers=headers, verify=False)
        response.raise_for_status()  # Raise an error for non-2xx status codes
        token = response.json().get("token")
        return token
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    aws_region_lists = ['ap-southeast-1', 'ap-southeast-3', 'ap-southeast-2']
    # Fetch username and password from environment variables
    username = os.getenv("PRISMA_USERNAME")
    password = os.getenv("PRISMA_PASSWORD")
    cwp_console_path = os.getenv("CWP_CONSOLE_PATH")
    if not (username and password and cwp_console_path):
        print("Error: Username or password or path to console not found in environment variables.")
        sys.exit()
    access_token = get_access_token(username=username, password=password, cwp_console_path=cwp_console_path)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    generate_pdf(aws_region_lists, cwp_console_path)
