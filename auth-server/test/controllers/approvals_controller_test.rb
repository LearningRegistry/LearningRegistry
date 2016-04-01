require 'test_helper'

# Functional test for the approval controller
class ApprovalsControllerTest < ActionController::TestCase
  include ApprovalTestUtils

  def setup
    User.all.map(&:destroy)
  end

  test 'creates a new approval form' do
    get :new

    assert_not_nil assigns(:approval)
  end

  test 'delivers a new approval' do
    session[:authenticated_email] = 'john@example.org'

    post :create, approval_form: approval_attributes

    assert_redirected_to new_approval_url
  end

  test 'raises an error if authenticated email is missing' do
    post :create, approval_form: approval_attributes

    assert_equal 'Authenticated e-mail is missing', flash.alert
    assert_template :new
  end

  test 'confirms a valid and current token' do
    assert_difference('User.count') do
      get :confirm, token: valid_token
    end

    assert_response :ok
  end

  test 'rejects an invalid token' do
    get :confirm, token: invalid_token

    error = JSON.parse(response.body)['error']

    assert_response :unprocessable_entity
    assert_equal 'Signature validation failed', error
  end

  test 'rejects an expired token' do
    get :confirm, token: expired_token

    error = JSON.parse(response.body)['error']

    assert_response :unprocessable_entity
    assert_equal 'Approval has already expired', error
  end

  test 'deletes a user when token is valid' do
    User.create(id: 'org.couchdb.user:me@example.org', name: 'me@example.org')

    assert_difference('User.count', -1) do
      get :delete, token: valid_token
    end

    assert_response :ok
  end
end
