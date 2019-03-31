from github import Github
import json, requests


def main(dict):
    url_param = dict.get("git_hub_api_url")
    user_param = dict.get("git_hub_username")
    repo_param = dict.get("git_hub_repo")
    zen_param = dict.get("zen_access_token")
    git_param = dict.get("git_hub_token")
    output = {}
    item = {}
    payload = {'access_token': zen_param}
    # Github Enterprise with custom hostname
    g = Github(user_param, git_param, base_url=url_param)
    # Then play with your Github objects:
    repo = g.get_repo(repo_param)
    repository_id = repo.id
    open_issues = repo.get_issues(state='open', assignee='richard-hopkins')
    for issue in open_issues:
        item = {}
        url = 'https://zenhub.ibm.com/p1/repositories/' + \
              str(repository_id) + \
              '/issues/' + \
              str(issue.number)
        response = requests.get(url, params=payload)
        json_data = response.json()
        pipeline = json_data['pipeline']['name']
        # print (pipeline + " - " + issue.title)
        item['name'] = issue.title
        item['pipeline'] = pipeline
        output[issue.number] = item
    #output_json = json.dumps(output)
    # print (output_json)
    return output

if __name__ == '__main__':
    empty_dict={}
    main(empty_dict)
