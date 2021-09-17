import json
import re

import httplib2
from oauth2client.service_account import ServiceAccountCredentials


class GoogleIndexationAPI:
    def __init__(self, key_file, urls_list):
        """
        :param  key_file: .json key Google API filename
        :param urls_list: .txt urls list filename
        """
        self.key_file = key_file
        self.urls_list = urls_list

    @staticmethod
    def choose_mode():
        """
        Choosing a mode: SAFE (1 domain processing) or SAFE (multi-domain processing)
        :return method: method name
        """
        while True:
            choose_msg = input('Choose one of modes and press Enter \n'
                               '1 - SAFE MODE (1 domain processing)\n'
                               '2 - PRO MODE (multi-domain processing)\n')
            if '1' in choose_msg:
                mode = 'SAFE'
                break
            elif '2' in choose_msg:
                mode = 'PRO'
                break
            else:
                print('Please enter correct number')

        print('You chose mode: ', mode)
        return mode

    @staticmethod
    def get_domain():
        """
        Input URL and strips it to a domain name (only in safe mode)
        :return stripped_domain:
        """
        domain = input('Enter domain you are going to work with: ')
        stripped_domain = re.sub(r'(https://)|(http://)|(www.)|/(.*)', '', domain)
        print(stripped_domain)
        return stripped_domain

    @staticmethod
    def choose_method():
        """
        Choosing a method for Google Indexing API request
        :return method: method name
        """
        while True:
            choose_msg = input('Choose one of methods (print number) and press Enter \n'
                               '1 - URL_UPDATED\n'
                               '2 - URL_DELETED:\n')
            if '1' in choose_msg:
                method = 'URL_UPDATED'
                break
            elif '2' in choose_msg:
                method = 'URL_DELETED'
                break
            else:
                print('Please enter correct number')

        print('You chose method: ', method)
        return method

    @staticmethod
    def get_domains(urls):
        """
        Get domains from URLs
        :param urls:
        :return _domains:
        """
        domains = set()
        for url in urls:
            domain = re.sub(r'(.*://)?([^/?]+).*', r'\1\2', url)
            domains.add(domain)
        return domains

    def get_urls(self, mode):
        """
        Gets URL list from a file and clean from not unique and not valid data
        :param mode:
        :return final_urls:
        """
        urls = []
        if mode == 'SAFE':
            domain = self.get_domain()
        else:
            domain = 'No Domain. You chose a PRO mode!'
        try:
            with open(self.urls_list, 'r', encoding='utf-8') as f:
                for line in f:
                    urls.append(line.strip())

                # Clean not unique urs
                urls = list(set(urls))
                domains = self.get_domains(urls)
                # Delete urls without ^http or which don't contain our domain name
                for url in urls.copy():
                    if 'http' not in url:
                        urls.pop(urls.index(url))
                    if (mode == 'SAFE') and (domain not in url):
                        urls.pop(urls.index(url))

                # 200 requests a day quota :(
                if len(urls) > 200:
                    print(f'You have a 200 request per day quota. You are trying to index {len(urls)}. ')

                    len_answer = input(f'I will make requests only for the first 200 urls. '
                                       f'Continue (YES/NO) ???\n')
                    if 'yes' in len_answer.lower():
                        final_urls = urls[0:199]
                        left_urls = urls[200:]

                        # Write urls over quota limit in file
                        with open('not_send_urls.txt', 'w', encoding='utf-8') as log:
                            for item in left_urls:
                                log.write(f'{item}\n')
                        print(f'There are {len(left_urls)} not send to Googlebot. \n'
                              f'Check not_send_urls.txt file in the script folder')

                    elif 'no' in len_answer.lower():
                        exit()
                    else:
                        print('Please enter correct answer (YES / NO)')
                else:
                    final_urls = urls

                if len(final_urls) < 1:
                    assert print('There are no urls in your file')
                    exit()

                return final_urls, domains

        except Exception as e:
            print(e, type(e))
            exit()

    def parse_json_key(self, domains, mode):
        """
        Parses and validates JSON.
        Prints information about domains and Google Search Console rights for API service account.
        """
        with open(self.key_file, 'r') as f:
            key_data = json.load(f)
            try:
                if mode == 'PRO':
                    print('Your domains: ', domains)
                input(f'Please add OWNER rights in GSC resource(s) to: {key_data["client_email"]} \nand press Enter')

            except Exception as e:
                print(e, type(e))
                exit()

    def single_request_index(self, url, method):
        """
        Makes a request to Google Indexing API with a selected method
        :param url:
        :param method:
        :return content:
        """
        api_scopes = ["https://www.googleapis.com/auth/indexing"]
        api_endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.key_file, scopes=api_scopes)

        try:
            http = credentials.authorize(httplib2.Http())
            r_content = """{""" + f"'url': '{url}', 'type': '{method}'" + """}"""
            response, content = http.request(api_endpoint, method="POST", body=r_content)
            return content

        except Exception as e:
            print(e, type(e))

    def indexation_worker(self):
        """
        Run this method after class instance creating.
        Gets an URL list, parses JSON key file, chooses API method,
        then sends a request for an each URL and logs responses.
        """
        mode = self.choose_mode()
        urls, domains = self.get_urls(mode)
        self.parse_json_key(domains, mode)
        method = self.choose_method()
        print('Processing... Please wait')
        with open('logs.txt', 'w', encoding='utf-8') as f:
            for url in urls:
                result = self.single_request_index(url, method)
                f.write(f'{url}: {result}\n')

        print(f'Done! We\'ve sent {len(urls)} URLs to Googlebot.\n'
              f'You can check responses in logs.txt')


if __name__ == '__main__':
    g_index = GoogleIndexationAPI('cred.json', 'urls.txt')
    g_index.indexation_worker()