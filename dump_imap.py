import os
import re
import argparse
import getpass
import imaplib
import email
import email.header
from datetime import datetime
from colorama import init, Style, Fore, Back

init(autoreset=True)

PATTERN_UID = re.compile(r'\d+ \(UID (?P<uid>\d+)\)')

argparser = argparse.ArgumentParser(
    description='Dump a IMAP folder into .eml files.')
argparser.add_argument('-s', '--server', dest='server',
                       help='IMAP server, like imap.gmail.com', required=True)
argparser.add_argument('-p', '--port', dest='port',
                       help='IMAP port', default=993, type=int)
argparser.add_argument('-u', '--username', dest='username',
                       help='IMAP username', required=True)
argparser.add_argument('-P', '--password', dest='password',
                       help='IMAP password', default=None)
argparser.add_argument('-r', '--remote-folder', dest='remote_folder',
                       help='Remote folder to download. You could inform multiple remote_folders by'
                            ' separating them with a comma', default='*')
argparser.add_argument('--list', dest='list',
                       help='List the remote folders and exit', nargs='?', const='list')
argparser.add_argument('-l', '--local-folder', dest='local_folder',
                       help='Absolute path of local folder where to save .eml files', default='.')
argparser.add_argument('-d', '--delete-remote', dest='delete_remote',
                       help='Should delete from remote folder?', nargs='?', const='delete')
argparser.add_argument('-t', '--trash-folder', dest='trash_folder', help='Remote trash folder name',
                       default='Trash')
args = argparser.parse_args()


def parse_uid(data):
    match = PATTERN_UID.match(data)

    return match.group('uid')


def fetch_message(mail, num):
    return mail.fetch(num, '(RFC822)')


def fetch_uid(mail, num):
    return mail.fetch(num, '(UID)')


def process(mail, folder):
    rv, data = mail.search(None, 'ALL')

    if rv != 'OK':
        raise FileNotFoundError('No messages found!', folder)

    print(Fore.BLUE + str(len(data[0])) + ' messages found!')

    if not os.path.isdir(args.local_folder):
        raise NotADirectoryError('Local folder not found.')

    for num in data[0].split():
        output_dir = os.path.abspath(args.local_folder)

        rv, data = fetch_message(mail, num)

        if rv != 'OK':
            raise OSError('Error getting message', num)

        try:
            msg = email.message_from_bytes(data[0][1])
        except:
            msg = email.message_from_string(data[0][1])

        subject = 'No subject'
        date = ''

        try:
            header = email.header.make_header(email.header.decode_header(msg['Subject']))

            subject = str(header)

            date_tuple = email.utils.parsedate_tz(msg['Date'])

            if date_tuple:
                datetime_ = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))

                date = datetime_.strftime('%Y-%m-%d %H:%M:%S') + ' - '
        except:
            pass

        subject = re.sub(r'(\n|\r|\r\n|\")', '', subject)
        subject = re.sub(r'/', '-', subject).strip()

        file = date + re.sub(r'(\<|\>|\$)', '', msg['Message-ID']) + ' - ' + subject

        print(Fore.BLUE + '\tWriting message at "' + file + '"... ', end='')

        final_dir = os.path.join(output_dir, folder.replace('"', ''))

        if not os.path.isdir(final_dir):
            os.makedirs(final_dir)

        with open('{}/{}.eml'.format(final_dir, file), 'wb') as f:
            f.write(data[0][1])

        print(Fore.GREEN + 'Done.', end='' if args.delete_remote is not None else '\n')

        if args.delete_remote is not None:
            delete(mail, num)


def delete(mail, num):
    print(Fore.RED + ' Deleting... ', end='')

    try:
        rv, data = fetch_uid(mail, num)
        msg_uid = parse_uid(data[0].decode())

        result = mail.uid('COPY', msg_uid, args.trash_folder)

        if result[0] == 'OK':
            mv, data = mail.uid('STORE', msg_uid, '+FLAGS', '(\\Deleted)')
            mail.expunge()

            print(Fore.RED + 'Ok.')
        else:
            print(Back.RED + Fore.BLACK + 'Failed!')
    except:
        return delete(mail, num)


def main():
    if args.password is None:
        args.password = getpass.getpass('IMAP password: ')

    mail = imaplib.IMAP4_SSL(args.server, args.port)

    try:
        mail.login(args.username, args.password)

        remote_folders = mail.list()[1]
        remote_folders_map = []

        for remote_folder in remote_folders:
            remote_folder = remote_folder.decode().split(' "." ')[1]

            remote_folders_map.append({
                'original': remote_folder,
                'lower': remote_folder.lower().strip()
            })

        if args.list is not None:
            for folder in remote_folders:
                print(folder.decode().split(' "." ')[1])
            return

        if args.remote_folder != '*':
            args.remote_folder = list(map(lambda x: x.strip(), str(args.remote_folder).lower().split(',')))

            diff = list(set(args.remote_folder) - set(list(map(lambda x: x['lower'], remote_folders_map))))

            if len(diff) > 0:
                raise AttributeError('Remote folders not found: ' + ', '.join(diff))

        for folder in args.remote_folder:
            folder = [f for f in remote_folders_map if f['lower'] == folder][0]['original']

            rv, data = mail.select(folder)

            if rv == 'OK':
                print(Fore.GREEN + 'Processing mailbox: ' + Fore.YELLOW + folder)

                process(mail, folder)

                mail.close()
            else:
                raise ConnectionError('Unable to open mailbox.', folder, rv)
    except BaseException as e:
        print(Back.RED + Fore.BLACK + '[ERROR]' + Style.RESET_ALL, Fore.RED + type(e).__name__, str(e.args))
    finally:
        mail.logout()

        print(Style.RESET_ALL)


if __name__ == '__main__':
    main()
