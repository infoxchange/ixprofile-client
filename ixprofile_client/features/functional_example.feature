Feature: Integrate with Profile Server

	As an admin
	I want to be able to login to the APPLICATION
	So that I can perform administrative tasks

    Background:
	    Given I have users in the database:
	      | email            | username | is_superuser |
	      | admin@domain.com | admin    | true         |
	    And I have users in the fake profile server:
	      | email                | subscribed |
	      | user1@profile.server | true       |
	      | user2@profile.server | false      |
	    And I do not have users in the fake profile server:
	      | email                   |
	      | new_user@profile.server |
        And I do not have users in the fake profile server:
          | username  |
          | new_user  |


    Scenario: Add a new user
	    When I log in to admin with email "admin@domain.com"
	    And I click "Users"
	    And I click "Add user"
	    And I fill in "email" with "<email>"
	    And I fill in "first_name" with "<first_name>"
	    And I fill in "last_name" with "<last_name>"
	    And I press "Save"
	    And I should see 'The user "<email>" was added successfully. You may edit it again below'
	    And I press "Save"
	    And I click "<email>"

	    Then the "Is active" checkbox should be checked
	    And the "Is staff" checkbox should not be checked
	    And the "Is superuser" checkbox should not be checked
	    And the email "<email>" exists in the fake profile server

    Examples:
        | email                   | first_name | last_name |
        | new_user@profile.server | New        | User      |
        | user1@profile.server    | Old        | User1     |
        | user2@profile.server    | Old        | User2     |
