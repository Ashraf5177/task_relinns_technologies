import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
print(OPENAI_API_KEY)
class WebsiteChatbot:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.website_content = ""
        self.structured_content = {}

    def scrape_website(self, url):
        """Scrapes content from given website URL and structures the information"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            self.structured_content = {
                'title': soup.title.string if soup.title else '',
                'headings': {},
                'main_content': []
            }
            
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                heading_text = heading.get_text().strip()
                next_paras = []
                for sibling in heading.find_next_siblings():
                    if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break
                    if sibling.name == 'p':
                        next_paras.append(sibling.get_text().strip())
                self.structured_content['headings'][heading_text] = next_paras

            for para in soup.find_all('p'):
                if not any(para.get_text().strip() in p_list for p_list in self.structured_content['headings'].values()):
                    self.structured_content['main_content'].append(para.get_text().strip())

            self.website_content = f"Title: {self.structured_content['title']}\n\n"
            for heading, paras in self.structured_content['headings'].items():
                self.website_content += f"Section - {heading}:\n{' '.join(paras)}\n\n"
            self.website_content += f"Additional Content:\n{' '.join(self.structured_content['main_content'])}"
            
            return True
        except Exception as e:
            print(f"Error scraping website: {e}")
            return False

    def process_user_input(self, user_input):
        """Processes user input and generates response using ChatGPT"""
        try:
            prompt = (
                f"Based on this structured website content:\n\n"
                f"{self.website_content}\n\n"
                f"Please provide a detailed and accurate answer to this question: {user_input}\n"
                f"If the answer cannot be found in the content, please say so."
            )
            print(prompt)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate answers based on website content. Use the structured content to provide relevant and specific information."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {e}"

def main():
    chatbot = WebsiteChatbot()
    url = input("Please enter the website URL: ")
    if not chatbot.scrape_website(url):
        print("Failed to scrape website. Exiting...")
        return

    print("\nWebsite content loaded! You can now ask questions about it.")
    print("Type 'quit' to exit")
    while True:
        user_input = input("\nYour question: ")
        if user_input.lower() == 'quit':
            break
            
        response = chatbot.process_user_input(user_input)
        print("\nChatbot:", response)

if __name__ == "__main__":
    main()
