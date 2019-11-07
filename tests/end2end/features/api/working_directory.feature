Feature: React to working directory changes

    Scenario: Monitor the current directory
        Given I open any directory
        Then there should be 1 monitored directory

    Scenario: Unmonitor the current directory
        Given I open any directory
        When I run set monitor_filesystem false
        Then there should be 0 monitored directories

    Scenario: Monitor the current image
        Given I open any image
        Then there should be 1 monitored file

    Scenario: Unmonitor the current image
        Given I open any image
        When I run set monitor_filesystem false
        Then there should be 0 monitored files
