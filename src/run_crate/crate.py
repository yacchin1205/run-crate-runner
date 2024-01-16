import datetime
import json
import os

def extract_notebook(crate):
    with open(crate) as f:
        data = json.load(f)
    entities = data['@graph']
    create_action_entities = [e for e in entities if e['@type'] == 'CreateAction']
    if len(create_action_entities) != 1:
        raise ValueError(f"Expected 1 CreateAction, found {len(create_action_entities)}")
    create_action = create_action_entities[0]
    if 'object' not in create_action:
        raise ValueError(f"CreateAction has no object")
    object_entities = create_action['object']
    if len(object_entities) != 1:
        raise ValueError(f"Expected 1 object, found {len(object_entities)}")
    object_entity = object_entities[0]
    return object_entity['@id']

def create(id, base_crate, input_notebook, output_notebook, start_time, exit_code, stdout, stderr):
    with open(base_crate) as f:
        base_crate = json.load(f)
    entities = base_crate['@graph']
    entities = [e for e in entities if e['@type'] != 'CreateAction']
    end_time = datetime.datetime.now()
    output_notebook_name = os.path.split(output_notebook)[1]
    action_entity = {
        '@id': f"#{id}",
        '@type': 'CreateAction',
        'actionStatus': 'CompletedActionStatus' if exit_code == 0 else 'FailedActionStatus',
        'endTime': end_time.isoformat(),
        'exitCode': exit_code,
        'name': f'Run notebook {id}',
        'object': [{
            '@id': input_notebook,
        }],
        'startTime': start_time.isoformat(),
        'subjectOf': [
            {
                '@id': f'stdout-{id}.log',
            },
            {
                '@id': f'stderr-{id}.log',
            },
        ],
    }
    if os.path.exists(output_notebook):
        action_entity['result'] = [{
            '@id': output_notebook_name,
        }]
    entities.append(action_entity)
    if os.path.exists(output_notebook):
        with open(output_notebook) as f:
            output_notebook_text = f.read()
        entities.append({
            '@id': output_notebook_name,
            '@type': 'File',
            'dateModified': end_time.isoformat(),
            'encodingFormat': 'application/json',
            'name': 'Output notebook',
            'text': output_notebook_text,
            'contentSize': len(output_notebook_text),
            'lineCount': len(output_notebook_text.splitlines()),
        })
    entities.append({
        '@id': f"stdout-{id}.log",
        '@type': 'File',
        'dateModified': end_time.isoformat(),
        'text': stdout,
        'lineCount': len(stdout.splitlines()),
        'contentSize': len(stdout),
        'encodingFormat': 'text/plain',
        'name': 'Notebook stdout',
    })
    entities.append({
        '@id': f"stderr-{id}.log",
        '@type': 'File',
        'dateModified': end_time.isoformat(),
        'text': stderr,
        'lineCount': len(stderr.splitlines()),
        'contentSize': len(stderr),
        'encodingFormat': 'text/plain',
        'name': 'Notebook stderr',
    })
    crate = {}
    crate.update(base_crate)
    crate['@graph'] = entities
    return crate
