'''
@filename: scrumpy.py
@author: smillerd
'''

import pandas as pd
import numpy as np
import datetime
import jira


class SprintReport:
    """class used to report on the progress in a given sprint, velocity in multiple sprints, etc.
    :param
    sprint : jira.resources.Sprint  : sprint that will be reported on throughout SprintReport
    """

    def __init__(self, jira_obj, sprint, start_date, sprint_length):
        self.jira_obj = jira_obj
        self.sprint = sprint
        self.sprint_id = sprint.id
        self.sprint_sequence = sprint.sequence

        # python jira package does not cover sprint start and end dates
        self.start_date = start_date
        self.sprint_length = sprint_length
        self.end_date = start_date + datetime.timedelta(days=sprint_length)
        self.end_date_str = str(self.end_date.year) + '-' + str(self.end_date.month) + '-' + \
                            str(self.end_date.day).zfill(2)

        # use this variable to set maxresults when calling jira.search_issues()
        self.maxresults = 10000

    def get_all_work(self):
        """retrieve all issues associated with a given sprint"""
        # todo -- allow project as a parameter
        jql_query = 'project = UEP AND issuetype = Story AND Sprint = ' + str(self.sprint_id)
        query_results = self.jira_obj.search_issues(jql_query, maxResults=self.maxresults)
        return query_results

    @property
    def all_work_df(self):
        return issue_df_from_list(self.get_all_work())

    def get_work_planned(self):
        """gets issues that were created on the day that the sprint started"""
        pass

    def get_work_accepted(self):
        """
        gets issues in self.sprint that are accepted
        """
        jql_query = 'project = UEP AND issuetype = Story AND status = Accepted AND resolved <= ' + self.end_date_str + \
                    ' AND Sprint = ' + str(self.sprint_id)
        query_results = self.jira_obj.search_issues(jql_query, maxResults=self.maxresults)
        return query_results

    def get_work_added_during_sprint(self):
        """gets issues that were added to the sprint after the day that the sprint started"""
        pass

    def get_work_unfinished_during_sprint(self):
        """gets issues that are part of sprint that are not accepted on or before the day the sprint closes"""
        jql_query = 'project = UEP AND issuetype = Story AND status in (Done, "In Progress", "Sprint Backlog") AND ' \
                    'Sprint = ' + str(self.sprint_id)
        query_results = self.jira_obj.search_issues(jql_query, maxResults=self.maxresults)
        return query_results

    @property
    def amount_work_planned(self):
        return len(self.get_all_work())

    @property
    def sprint_state(self):
        return self.sprint.state

    @property
    def percent_forecast_met(self):
        """
        Public attribute that represents the number of issues accepted versus the number of issues originally
        planned
        """
        pct = float(len(self.get_work_accepted())) / float(len(self.get_all_work()))
        return pct

    @property
    def velocity(self):
        """Public attribute that represents the number of issues complete during a sprint"""
        return len(self.get_work_accepted())

    @property
    def percent_project_complete(self):
        """
        Public attribute that represents the number of issues accepted out of the number of issues remainng in
        the project at the end of the sprint
        """
        return np.nan

    @property
    def cards_remaining_in_backlog(self):
        """at the end of the sprint, how many issues remain in the backlog"""
        return np.nan

    @property
    def time_left_at_velocity(self):
        """the number of sprints remaining until all issues in backlog are resolved, at current velocity"""
        return np.nan

    @property
    def sprint_report_dict(self):
        return {'sprint': self.sprint.name, 'state': self.sprint_state, 'start_date': self.start_date,
                'end_date':self.end_date, 'planned': self.amount_work_planned, 'velocity': self.velocity,
                'percent_forecast_met': self.percent_forecast_met
                }


class ClientReport:
    """
    Find all issues flagged "report_to_client". Collect information, format into csv, export to outfile

    :parameter
    project_board : jira.resources.Board
        jira project that the search is associated with
    """

    def __init__(self, project_board, jira_obj, maxresults=10000):
        self.project_board = project_board
        self.jira_obj = jira_obj
        self.maxresults = maxresults

    def get_client_issues(self):
        """
        form JQL query and search for issues with tag \"report_to_client\". Return list of jira.resources.Issue type
         """
        query = 'project = UEP AND issuetype = Bug AND status = "Sprint Backlog" AND labels = Asks_For_Client'
        query_results = self.jira_obj.search_issues(query, maxResults=self.maxresults)
        return query_results

    @property
    def issue_detail(self):
        """public property collect parts of jira card that are required for client_csv. return pd.DataFrame"""
        # create empty dataframe to populate with data
        issue_detail_df = pd.DataFrame(columns=['Issue', 'Client_Lead', 'AQN_Lead', 'Description', 'Impact',
                                                'Detailed_Status', 'Next_Steps', 'Date_First_Raised', 'Impediment_Date',
                                                'Last_Updated', 'Priority', 'key', 'id'])

        # iterate through issues, save relevant details to dataframe
        for issue in self.get_client_issues():
            issue_dict = {'Issue': issue.fields.summary,
                          'Client_Lead': issue.fields.customfield_10036,
                          'Description': issue.fields.customfield_10031,
                          'Impact': issue.fields.customfield_10032,
                          'Detailed_Status': issue.fields.customfield_10033,
                          'Next_Steps': issue.fields.customfield_10038,
                          'Date_First_Raised': issue.fields.customfield_10035,
                          'Last_Updated': issue.fields.updated,
                          'Impediment_Date': issue.fields.customfield_10034,
                          'Priority': issue.fields.priority,
                          'key': issue.key, 'id': issue.id,
                          }
            if issue.fields.assignee:
                issue_dict['AQN_Lead'] = issue.fields.assignee.displayName
            else:
                issue_dict['AQN_Lead'] = np.nan
            s = pd.Series(issue_dict)
            issue_detail_df = issue_detail_df.append(s, ignore_index=True)
        return issue_detail_df

    def send_to_csv(self, outfile):
        """send client report to outfile (.csv)"""
        df = self.issue_detail
        df.to_csv(outfile)
        return None


class EpicReport:
    """
    class to report on the status of an epic as of a given date
    :parameter
        epic_name : str
            string of epic name used to find associated issues. Note: requires custom Jira setup to properly find
            issues, and does not use embedded Epic features
    """

    def __init__(self, jira_obj, report_date, epic_name, maxresults=10000):
        self.jira_obj = jira_obj
        self.epic_name = epic_name

        # use to filter issues for only those that were completed by the report date
        self.report_date = report_date
        self.report_date_str = str(self.report_date.year) + '-' + str(self.report_date.month) + '-' + \
                               str(self.report_date.day).zfill(2)

        # used for limiting query results from jira.search_issues()
        self.maxresults = maxresults

    @property
    def get_epic_subtasks(self):
        """return list of jira issues associated with the epic"""
        epic_query = 'project = UEP AND issuetype = Story AND "Associated Epic" ~ "%s"' % self.epic_name
        query_result = self.jira_obj.search_issues(epic_query, maxResults=self.maxresults)
        return query_result

    @property
    def all_work_df(self):
        return issue_df_from_list(self.get_epic_subtasks())

    @property
    def epic_issue_done_by_date(self):
        """return list of issue_id and Bool indicating whether issue was complete before or on report_date"""
        query = 'project = UEP AND issuetype = Story AND "Associated Epic" ~ "' + self.epic_name + '" AND resolved <= '\
                + self.report_date_str
        query_result = self.jira_obj.search_issues(query, maxResults=self.maxresults)
        return query_result

    @property
    def percent_complete(self):
        """return the percent of issues_done_by_date that are true"""
        return float(len(self.epic_issue_done_by_date)) / float(len(self.get_epic_subtasks))


class EffortReport:
    """
    class to report on the status of an effort as of a given date
    """

    def __init__(self, jira_obj, report_date, effort_label, maxresults=10000):
        self.jira_obj = jira_obj

        if effort_label is None:
            self.effort_label = '99999999999999'
        else:
            self.effort_label = effort_label

        # use to filter issues for only those that were completed by the report date
        self.report_date = report_date
        self.report_date_str = str(self.report_date.year) + '-' + str(self.report_date.month) + '-' + \
                               str(self.report_date.day).zfill(2)

        # use maxresults to set the maximum length of jira.search_issue() response
        self.maxresults = maxresults

    @property
    def get_effort_subtasks(self):
        """return jira issues associated with the effort"""
        query = 'project = UEP AND issuetype = Story AND labels = ' + self.effort_label
        query_result = self.jira_obj.search_issues(query, maxResults=self.maxresults)
        return query_result

    @property
    def all_work_df(self):
        return issue_df_from_list(self.get_effort_subtasks())

    @property
    def effort_issue_accepted_by_date(self):
        """return list of issue_id and Bool indicating whether issue was complete before or on report_date"""
        query = 'project = UEP AND issuetype = Story AND resolved <= ' + self.report_date_str + ' AND labels = ' \
                + self.effort_label
        query_result = self.jira_obj.search_issues(query, maxResults=self.maxresults)
        return query_result

    @property
    def effort_percent_complete(self):
        """return the percent of issues_done_by_date that are true"""
        return float(len(self.effort_issue_accepted_by_date)) / float(len(self.get_effort_subtasks))


class DailyReport:
    """
    generate daily information relevant to the current sprint, save to csv
    """
    def __init__(self, jira_obj, board, end_sprint=False):
        self.jira_obj = jira_obj
        self.end_sprint = end_sprint

        self.today = datetime.datetime.today()
        self.this_sprints_monday = self.today - datetime.timedelta(days=self.today.weekday())
        self.last_monday = self.this_sprints_monday - datetime.timedelta(weeks=1)
        self.prior_monday = self.last_monday - datetime.timedelta(weeks=1)

        self.board = board

        # self.sprint_id = current_sprint_id
        # self.sprint = jira.sprint(current_sprint_id)

    @property
    def sprints_on_board(self):
        return self.jira_obj.sprints(self.board.id)

    @property
    def current_sprint(self):
        return self.sprints_on_board[-1]

    @property
    def current_sprint_report(self):
        sr = SprintReport(jira_obj=self.jira_obj, sprint=self.current_sprint, start_date=self.this_sprints_monday,
                          sprint_length=5)
        return sr

    @property
    def last_sprint(self):
        return self.sprints_on_board[-2]

    @property
    def last_sprint_report(self):
        sr = SprintReport(jira_obj=self.jira_obj, sprint=self.last_sprint, start_date=self.last_monday,
                          sprint_length=5)
        return sr

    @property
    def prior_sprint(self):
        return self.sprints_on_board[-3]

    @property
    def prior_sprint_report(self):
        sr = SprintReport(jira_obj=self.jira_obj, sprint=self.prior_sprint, start_date=self.prior_monday,
                          sprint_length=5)
        return sr

    @property
    def historic_sprint_report_df(self):
        return pd.DataFrame()

    @property
    def epic_report_df(self):
        data_dict = {'date': self.today}
        avail_epics = []
        for issue in self.current_sprint_report.get_all_work():
            if issue.fields.customfield_10029 not in avail_epics:
                avail_epics.append(issue.fields.customfield_10029)
        for epic in avail_epics:
            if epic is not None:
                er = EpicReport(self.jira_obj, self.today, epic)
                data_dict[er.epic_name] = er.percent_complete
        return pd.DataFrame(data_dict, index=[0])

    @property
    def effort_report_df(self):
        data_dict = {'date': self.today}
        avail_efforts = []
        for issue in self.current_sprint_report.get_all_work():
            for label in issue.fields.labels:
                if label not in avail_efforts:
                    avail_efforts.append(label)
        for effort in avail_efforts:
            if effort is not None:
                er = EffortReport(self.jira_obj, self.today, effort)
                data_dict[er.effort_label] = er.effort_percent_complete
        return pd.DataFrame(data_dict, index=[0])


def issue_df_from_list(issues_list):
    df = pd.DataFrame(columns=['date', 'key', 'id', 'summary', 'epic', 'effort', 'definition_of_done', 'story_points',
                               'priority', 'status'])
    for issue in issues_list:
        data_dict = {'date': datetime.datetime.today(), 'key': issue.key, 'id': issue.id, 'summary': issue.fields.summary,
                     'epic': issue.fields.customfield_10029, 'effort': issue.fields.labels,
                     'definition_of_done': issue.fields.customfield_10028,
                     'story_points': issue.fields.customfield_10027,
                     'priority': issue.fields.priority.name, 'status': issue.fields.status.name}

        df = df.append(data_dict, ignore_index=True)
    df.reset_index(inplace=True)
    return df

