require 'test_helper'

# Test for a CouchDB user
class UserTest < ActiveSupport::TestCase
  include ApprovalTestUtils

  def setup
    User.all.map(&:destroy)

    @user = User.create(id: 'org.couchdb.user:me@example.org',
                        name: 'me@example.org',
                        password: 'passwd')
  end

  test '::get_auth_session' do
    auth_session = User.get_auth_session('me@example.org', 'passwd')

    assert_not_nil auth_session
  end

  test 'raises exception when credentials are not valid' do
    assert_raises RestClient::Unauthorized do
      User.get_auth_session('invalid@example.org', 'invalid')
    end
  end
end
