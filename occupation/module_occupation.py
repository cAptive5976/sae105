from datetime import datetime

"""
.. module:: module_occupation
   :platform: Unix
   :synopsis: module pour extraire les données des fichiers icalandar

.. moduleauthor::  William <>   Charles <>


"""

def extract_data(file_list):
    """Ouvre les fichiers et les lit.

    :param file_list: Liste des chemins des fichiers à lire.
    :type file_list: List[str]
    :return: Liste des contenus des fichiers.
    :rtype: List[str]
    """
    data = []
    for file_path in file_list:
        with open(file_path, 'r', encoding='utf-8') as file:
            data.append(file.read())
    return data

def process_data(data):
    """Traite les données extraites du fichier iCalendar (ICS).

    :param data: Liste des contenus des fichiers iCalendar.
    :type data: List[str]
    :return: Liste d'événements traités avec les détails pertinents.
    :rtype: List[Dict[str, Any]]
    """
    processed_data = []

    for ics_content in data:
        lines = ics_content.split('\n')
        events = []
        current_event = None

        for line in lines:
            if line.startswith('BEGIN:VEVENT'):
                current_event = {}
            elif line.startswith('SUMMARY:'):
                current_event['summary'] = line.split(':')[-1]
            elif line.startswith('LOCATION:'):
                current_event['location'] = line.split(':')[-1]
            elif line.startswith('DTSTART:'):
                start_time = line.split(':')[-1]
                current_event['start_time'] = datetime.strptime(start_time, '%Y%m%dT%H%M%SZ')
            elif line.startswith('DTEND:'):
                end_time = line.split(':')[-1]
                current_event['end_time'] = datetime.strptime(end_time, '%Y%m%dT%H%M%SZ')
            elif line.startswith('END:VEVENT'):
                events.append(current_event)
        processed_data.extend([event for event in events if event.get('summary', '')])
    return processed_data

def generate_html(data, output_dir):
    """Génère un fichier HTML à partir des données traitées.

    :param data: Liste d'événements traités.
    :type data: List[Dict[str, Any]]
    :param output_dir: Répertoire de sortie pour le fichier HTML généré.
    :type output_dir: str
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>I-calendar : occupation des salles</title>
        <link rel="stylesheet" type="text/css" href="css/index.css" />
        <link rel="icon" type="img/png" href="images/icon.png" />
    </head>
    <body>
    <header>
        <h1>SAE105 : Traiter des données</h1>
    </header>
        <h2>I-calendar : occupation des salles</h2>
        <table border="1">
            <tr>
                <th>Salle</th>
                <th>Heures d'utlisation</th>
                <th>Heures d’utilisation moyen/semaine</th>
                <th>Heures d’utilisation moyen/jour</th>
                <th>Taux d’occupation (%)</th>
            </tr>
    """

    processed_locations = set()
    for event in data:
        location = event['location']
        if location in processed_locations  or location == '' or location == 'salle-non-renseignée-IUT86-Chatel':
            continue
        total_hours = sum((event['end_time'] - event['start_time']).total_seconds() / 3600 for event in data if event['location'] == location)
        processed_locations.add(location)
        html_content += f"""    
        <tr>
            <td>{location}</td>
            <td>{total_hours}</td>
            <td>{round(total_hours / 7, 2)}</td>
            <td>{round(total_hours / len(data), 2)}</td>
            <td>{round((total_hours / len(data)) * 100, 2)}%</td>
        </tr>
    """

    html_content += """
        </table>
        <footer>
        PS : Certaines cases sont buggées du fait que les salles ne sont pas forcément remplies
        <br></br>
        Projet realisé par  Charles et  William
        </footer>
    </body>
    </html>
    """

    with open(output_dir + 'index.html', 'w', encoding='utf-8') as file:
        file.write(html_content)
