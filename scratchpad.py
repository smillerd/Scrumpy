import pandas as pd
import numpy as np
import jira
import scrumpy
import datetime

# authenticate, connect to project
user = 'smillerd@aqnstrategies.com'
password = 'cachet-wench-jupiter'
j = jira.JIRA('https://aqnstrategies.atlassian.net', auth=(user, password))

# specify project board to consider
boards = j.boards()
uep_board = boards[1]
uep_board_id = boards[1].id

# get sprints associated with board
sprints = j.sprints(uep_board_id)

# issue_68 = j.issue('UEP-68')
# sprint_1 = sprints[0]
# print(sprint_1)
sprint_4 = sprints[3]

start_date = datetime.date(2018, 10, 9)
end_date = start_date + datetime.timedelta(days=8)
end_date_str = str(end_date.year) + '-' + str(end_date.month) + '-' + str(end_date.day).zfill(2)
sr = scrumpy.SprintReport(j, sprint_4, start_date, 8)

# q = 'project = UEP AND issuetype = Story AND Sprint = ' + str(sprint_1.id)
# res = j.search_issues(q, maxResults=10000)

# assert res == sr.get_all_work()
# print('1. Success! \n')
#
#
# # test functionality of getting work accepted from a given sprint
# # note: this does not mean the work was accepted during the sprint
# q1 = 'project = UEP AND issuetype = Story AND status = Accepted AND resolved <= ' + end_date_str + ' AND Sprint = ' \
#      + str(sprint_1.id)
# res1 = j.search_issues(q1, maxResults=10000)
# assert res1 == sr.get_work_accepted()
# print('2. Success! \n')
#
#
# q2 = 'project = UEP AND issuetype = Story AND status in (Done, "In Progress", "Sprint Backlog") AND Sprint = ' + \
#      str(sprint_1.id)
# res2 = j.search_issues(q2, maxResults=10000)
# assert res2 == sr.get_work_unfinished_during_sprint()
# print('3. Success! \n')
#
# q3 = 'project = UEP AND issuetype = Story AND status = "Sprint Backlog"'
# res3 = j.search_issues(q3, maxResults=10000)
# # assert res3 == sr.cards_remaining_in_backlog
# print('4. Success! \n')
#
#
# sr2 = scrumpy.SprintReport(j, sprints[1], datetime.date(2018, 10, 18), 11)
# print(sr2.percent_forecast_met)


# q4 = 'project = UEP AND issuetype = Bug AND status = "Sprint Backlog" AND labels = Asks_For_Client'
# res4 = j.search_issues(q4, maxResults=10000)
#
# issue_detail_df = pd.DataFrame(columns=['Issue', 'Client_Lead',  'AQN_Lead', 'Description', 'Impact', 'Detailed_Status',
#                                         'Date_First_Raised', 'Impediment_Date', 'Priority', 'Last_Updated', 'key',
#                                         'id', ])
# for issue in res4:
#     issue_dict = {'Issue': issue.fields.summary,
#                   'Client_Lead': issue.fields.customfield_10036,
#                   'Description': issue.fields.customfield_10031,
#                   'Impact': issue.fields.customfield_10032,
#                   'Detailed_Status': issue.fields.customfield_10033,
#                   'Date_First_Raised': issue.fields.customfield_10035,
#                   'Impediment_Date': issue.fields.customfield_10034,
#                   'Priority': issue.fields.priority,
#                   'Last_Updated': issue.fields.updated,
#                   'key': issue.key, 'id': issue.id,
#                   }
#     if issue.fields.assignee:
#         issue_dict['AQN_Lead'] = issue.fields.assignee.displayName
#     else:
#         issue_dict['AQN_Lead'] = np.nan
#     print(issue_dict)
#     s = pd.Series(issue_dict)
#     issue_detail_df = issue_detail_df.append(s, ignore_index=True)
#
# cr = scrumpy.ClientReport(uep_board, j)
# assert len(issue_detail_df.columns.values) == len(cr.issue_detail.columns.values)
# assert set(issue_detail_df.columns.values).issubset(set(cr.issue_detail.columns.values))
# assert set(issue_detail_df.columns.values).issuperset(set(cr.issue_detail.columns.values))
# # assert issue_detail_df.sum().sum() == cr.issue_detail.sum().sum()
#
# print('Sending to csv.')
# cr.send_to_csv('test_file.csv')
# print('Done.')

# # test EpicReport functionality
# er = scrumpy.EpicReport(j, datetime.date(2018, 11, 6), 'niat_estimator')
#
# # start by testing associated subtasks
# q5 = 'project = UEP AND issuetype = Story AND "Associated Epic" ~ "%s"' % 'niat_estimator'
# res5 = j.search_issues(q5, maxResults=10000)
#
# assert res5 == er.get_epic_subtasks
#
# # start by testing accepted issues
# q6 = 'project = UEP AND issuetype = Story AND "Associated Epic" ~ "niat_estimator" AND resolved <= 2018-11-06'
# res6 = j.search_issues(q6, maxResults=10000)
#
# assert res6 == er.epic_issue_done_by_date


# create effort_report to test effort_report functionality
# effort_report = scrumpy.EffortReport(j, datetime.date(2018, 11, 6), 'DualValidation')
#
# q7 = 'project = UEP AND issuetype = Story AND labels = DualValidation'
# res7 = j.search_issues(q7, maxResults=10000)
#
# assert res7 == effort_report.get_effort_subtasks
#
#
# q8 = 'project = UEP AND issuetype = Story AND resolved <= 2018-11-06 AND labels = DualValidation'
# res8 = j.search_issues(q8, maxResults=10000)
#
# assert res8 == effort_report.effort_issue_done_by_date

# dr = scrumpy.DailyReport(j, uep_board)
# # print('dr.current_sprint:', dr.current_sprint)
# # print('type(dr.current_sprint):', type(dr.current_sprint))
# # print('sprints[-1]:', sprints[-1])
# # print('type(sprints[-1]):', type(sprints[-1]))
# assert dr.current_sprint.id == sprints[-1].id
# assert dr.last_sprint.id == sprints[-2].id
# assert dr.prior_sprint.id == sprints[-3].id


# print(dr.epic_report_df.head())

# print(dr.effort_report_df.columns.values)


# issues_list = sr.get_all_work()


def issue_df_from_list(issue_list):
    df = pd.DataFrame(columns=['date', 'key', 'id', 'summary', 'epic', 'effort', 'definition_of_done', 'story_points',
                               'priority', 'status'])
    for issue in issue_list:
        data_dict = {'date': datetime.datetime.today, 'key': issue.key, 'id': issue.id,
                     'summary': issue.fields.summary,
                     'epic': issue.fields.customfield_10029, 'effort': issue.fields.labels,
                     'definition_of_done': issue.fields.customfield_10028,
                     'story_points': issue.fields.customfield_10027,
                     'priority': issue.fields.priority.name, 'status': issue.fields.status.name}

        df = df.append(data_dict, ignore_index=True)
    df.reset_index(inplace=True)
    return df



