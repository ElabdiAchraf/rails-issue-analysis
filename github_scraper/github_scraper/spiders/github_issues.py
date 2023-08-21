import scrapy
from bs4 import BeautifulSoup

class GitHubIssuesSpider(scrapy.Spider):
    name = "github_issues"
    start_urls = ['https://github.com/rails/rails/issues'] 

    issue_count = 0

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        
        for issue in soup.select('.js-navigation-item'):
            title_link = issue.select_one('.js-navigation-open')
            if title_link and self.issue_count < 500:
                # Directly extract data available in the main issue list
                data = {
                    'title': title_link.text.strip(),
                    'link': response.urljoin(title_link['href']),
                    'labels': [label.text for label in issue.select('.IssueLabel')],
                }
                
                # Move to individual issue's page to extract more details
                yield scrapy.Request(data['link'], callback=self.parse_issue, meta=data)

                self.issue_count += 1
            elif self.issue_count >= 500:
                break
        
        # Pagination, only if we have less than 500 issues
        if self.issue_count < 500:
            next_page = soup.select_one('.next_page')
            if next_page and not next_page.has_attr('disabled'):
                yield scrapy.Request(response.urljoin(next_page['href']), callback=self.parse)

    def parse_issue(self, response):
        # Parsing individual issue's page
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extracting creation date, issue submitter, and comments
        timestamp = soup.select_one('relative-time')
        issue_submitter = soup.select_one('a.author')
        comment_authors = [author.text.strip() for author in soup.select('.timeline-comment-group .author')]
        number_of_comments = len(comment_authors)

        # Collecting data
        data = response.meta
        data['creation_date'] = timestamp['datetime'] if timestamp else None
        data['issue_submitter'] = issue_submitter.text.strip() if issue_submitter else None
        data['body'] = soup.select_one('.js-comment-body').text.strip() if soup.select_one('.js-comment-body') else None
        data['number_of_comments'] = number_of_comments
        data['comment_authors'] = comment_authors

        yield data
