require 'test_helper'

class SessionsControllerTest < ActionController::TestCase
  def setup
    OmniAuth.config.test_mode = true
    OmniAuth.config.add_mock(:google, info: { email: 'user@example.org' })
    request.env['omniauth.auth'] = OmniAuth.config.mock_auth[:google]
    request.env['omniauth.params'] = { back_url: 'http://example.org' }
  end

  def teardown
    OmniAuth.config.mock_auth[:google] = nil
  end

  test 'returns a 400 Bad Request error when the back url param is not set' do
    get :new, provider: 'google'

    assert_response :unprocessable_entity
    assert_equal 'Back url is missing', JSON.parse(response.body)['error']
  end

  test 'stores the back url and redirects to the authorization endpoint' do
    get :new, provider: 'google', back_url: 'http://example.com'

    assert_equal 'http://example.com', session[:back_url]
    assert_redirected_to '/auth/google'
  end

  test 'redirects to approval form when user is not found' do
    User.stub :exists?, false do
      get :create, provider: 'google'
    end

    assert_redirected_to new_approval_url
  end

  test 'sets the session with the user when already has an account' do
    session[:back_url] = 'http://example.org'

    User.stub :exists?, true do
      User.stub(:get_auth_session, '12345ABC') do
        get :create, provider: 'google'
      end
    end

    assert_equal 'user@example.org', session[:user_id]
    assert_equal '12345ABC', cookies['AuthSession']
    assert_redirected_to 'http://example.org'
  end

  test 'renders the couchdb login form when auth session is not available' do
    session[:back_url] = 'http://example.org'

    User.stub :exists?, true do
      User.stub(:get_auth_session, false) do
        get :create, provider: 'google'
      end
    end

    assert_redirected_to sessions_couchdb_new_url
  end

  test 'redirects to the back url when couchdb login succeeds' do
    session[:back_url] = 'http://example.org'

    User.stub(:get_auth_session, '12345ABC') do
      post :couchdb_login
    end

    assert_redirected_to 'http://example.org'
  end

  test 'renders the couchdb login form when password is incorrect' do
    User.stub(:get_auth_session, false) do
      post :couchdb_login
    end

    assert_template :couchdb_new
    assert_equal 'Password is not correct', flash.alert
  end

  test 'returns the current session when the user has logged in' do
    session[:user_id] = 'user@example.org'

    get :current

    assert_equal 'user@example.org', JSON.parse(response.body)['email']
  end

  test 'returns a 401 Unauthorized status when session is not available' do
    session[:user_id] = nil

    get :current

    assert_response :unauthorized
  end

  test 'destroys the active session when the user logs out' do
    get :destroy

    assert_response :ok
    assert_nil session[:user_id]
  end
end
