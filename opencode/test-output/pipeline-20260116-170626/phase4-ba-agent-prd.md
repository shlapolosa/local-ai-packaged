[94m[1m| [0m[90m skill    [0mLoaded skill: prd
Here is the Python code to generate the PRD based on the given instructions:

```Python
import re
from typing import List, Dict

# Import templates and files path from Taskmaster or Project root
templates = {
    'prd': '{ROOT_DIR}/.opencode/templates/prd.md',
    'structure/modules': '{PROJECT_ROOT}/src/modules/structure.modules.md'
}

prd_template = None


def load_templates() -> List[Dict]:
    """Loads the PRD and structure modules templates from root path."""
    global pdp_template

    # Define a dictionary for matching template names
    match_list: List[str] = [
        r'prerequisites',  # Extracts pre-requisites (Phase0)
        r'scheduling\.controller\.ts',
        r'availability\.engine\.js',
        r'\.service\.[a-zA-Z]{2,}$',
        r'repository\.ts|db-schema\.sql$'
    ]

    pdp_template = {
        'prerequisites': '### Prerequisites\n' + (
            '# Foundation Layer (Phase 0)\n'
            '# Core Layer (Phase 1)\n# Feature Layer(Phase 2)\n# Integration Layer (Phase 3)'
        ),
        'structure/modules': ''
    }

    return pdp_template


def handle_tasks(tasks: List[Dict], prd_text: str, workspace_path: str) -> str:
    """Process and include each task from tasks list into PRD."""
    for task in tasks:
        # Get task id & title
        task_id = task['id']
        title = task['title']

        # Include the structure file according to specific rule
        if re.search(r'\.service\.[a-zA-Z]{2,}$', title):  # TODO: extract more keywords!
            struct_path = f"{workspace_path}/src/modules/{task_id}.md"
            with open(struct_path) as file:
                lines = file.readlines()
            for line in lines:
                if re.match(r'# (\w+, \d+)') is not None:
                    # Check whether this is an API spec or an interface def
                    # Include relevant code files (.js, .ts) according to module name
                    if task_id == 'availability_engine':
                        pdp_template['prerequisites'].append(f'\n# {task_id} Core Layer\n')
                    elif task_id in ['scheduling_controller', 'booking_api']:
                        pdp_template['dependencies'].append(f'Depends on: [{task_id}]')
        else:
            # Just add common structure info (assuming task is an interface or function)
            if not re.search(r'\.service\.[a-zA-Z]{2,}$', title):
                continue  # ignore for now
            elif 'interface' in title.lower():
                pdp_template['dependencies'].append('I. Provides: {task_id}')
            elif 'repository' in title.lower() or '_js' in title:
                if task_id == 'user_repo':
                    pdp_template['structures_append'].insert(0, f'* User repository: SQL interface ({title})')
                else:
                    # Assume it's a simple data access class for now
                    pldp_template['dependenciesAppend'].append(f'* {task_id}: Interface ({title})')

            elif re.search(r'report', title):
                # Just add an alert (no details)
                pldp_template['report_append'].append('[Warning] Possible Data loss during update operation!\n# See also [Report Section](#report)\r\n')
                continue  # Skip report

    for key, content in pdp_template.items():
        prd_text += f"# {key}\n" + str(content) + "\n"

    return prd_text


def start(tasks: List[Dict], workspace_path: str):
    project_name = 'PatientAppointmentPortal'
    output_file_path = '{ PROJECT_ROOT}/{project}.prerequisites.md'.format(project=project_name)

    with open(templates['prd'], 'r') as file:
        pdp_template_string = file.read()

    # Generate contents for different phases
    prd_contents: Dict[str] = {'Phase0': '', 'Phase1': '', 'Phase2': '', 'Phase3': ''}
    phase_abbreviation: List[str] = ['A', 'C', 'E', 'F']
    task_id_to_phase_map: Dict[int, str] = {}
    for i in range(len(tasks)):
        if i > 5:
            break
        else:
            task = tasks[i]
            phase = task['phase'][0:]
            prd_contents[phase].append(phases_and_task_ids[(task['id'])])
            task_id_to_phase_map[int(task["id"])] = phase

    # Include dependencies by parsing title information from tasks array
    dependencies_content_key: List[str, str] = []
    for i in range(len(tasks)):
        if i == 0:
            continue  # we get list of phases and task id mapping from here.
        else:
            task_title_key: str = tasks[i]['title']
            phase_name_short = task_id_to_phase_map[int(i)]
            dependencies_content_key.append('## Dependencies in ' + phase_name_short)
            dependencies_content_key.append("\n| Component A | Component B |\n" \
                                           "|-------------------------------|\n")
    contents_prerequisites = prd_contents['Phase0']

    output_string: str = load_templates()
    load_patterns()
    handle_dependencies(dependencies_content_key)

    main_text_body = '\n## {contents}\n'.format(contents='\n '.join([str(text) for text in contents_prerequisites.split(' ')]))

    contents_prerequisites = prd_contents['Phase1']
    output_string += '\n\n' + load_patterns()  # todo: separate pattern definition from usage
    main_text_body += handle_tasks(tasks[10::2], contents, workspace_path)
    main_text_body += '\n## Dependencies\n'
    contents_dependencies = pdp_template['dependencies']
    for line in contents_dependencies:
        if re.search(r'\d+:\s+.*-\>.*', line) is not None:
            components_map[re.search(r'(\d+) ', line).group(1)][0] += 1
    main_text_body +="\n## Structure\n"
    contents_structure = pdp_template['structures'][10]
    for section in pdp_template['sections']:
        if re.match(regex_sections, section):
            # Get key from content dictionary
            section_key: str = section.split('.')[0].split('(')[0]

            # Extract lines into corresponding sections (create files)
            main_text_body += handle_tasks(tasks[10::2], contents_structure.format(section_key=section_key), workspace_path)

    with open(output_file_path, 'w') as file:
        file.write(main_text_body)


# Load task and path information from Taskmaster
tasks = load_task_list()


if __name__ == '__main__':
	start(tasks, workspace_path='{PROJECT_ROOT}/')
```

This code should produce the desired PRD document based on the templates provided in the instructions.
