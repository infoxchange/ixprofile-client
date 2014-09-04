@integration @profiles
Feature: Login to the APPLICATION as an admin user with my single sign on token

    As an admin
    I want to be able to login to the APPLICATION with my single-signon token
    So that I can perform administrative tasks

    Background:
        Given I have a fresh web browser
        And Given I have users in the database:
            | email            | username | is_superuser |
            | admin@domain.com | admin    | true         |
            | user@domain.com  | user     | false        |
        And I have users in the real profile server:
            | email            | subscribed |
            | admin@domain.com | true       |
            | user@domain.com  | true       |
            | guest@domain.com | false      |

        And I do not have users in the real profile server:
            | email             |
            | nouser@domain.com |


    Scenario: log in via profile server with a user with admin permissions
        When I visit site page "admin"
        And I log in to the real profile server with username "admin" and password "password"

        Then I should see "Welcome Admin"
        And users should be present in the database:
            | username | email            | first_name | last_name |
            | admin    | admin@domain.com | Admin      | Test      |


    Scenario: log in via profile server with a user without admin permissions
        When I visit site page "admin"
        And I log in to the real profile server with username "user" and password "password"

        Then I should not see "Welcome User"


    Scenario: Non-admin user can login into the site but cannot reach the admin interface
        When I visit site page "/login"
        And I log in to the real profile server with username "user" and password "password"
        And I should not see "Welcome User"

        When I visit site page "admin"
        Then I should not see "Welcome User"


    Scenario: log in via profile server with a user not subscribed to the APPLICATION
        When I visit site page "admin"
        And I log in to the real profile server with username "guest" and password "password"

        Then I should not see "Welcome Guest"
