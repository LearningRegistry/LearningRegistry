# Controller that gets called after the user has authenticated with a provider
class SessionsController < ApplicationController
  def new
    check_params
    return if performed?

    session[:back_url] = params[:back_url]

    redirect_to "#{app_sub_uri}/auth/#{params[:provider]}"
  end

  def create
    if User.exists?(email)
      session[:user_id] = email
      log_user_into_couchdb

      redirect_to session[:back_url]
    else
      session[:authenticated_email] = email

      redirect_to new_approval_url
    end
  end

  def destroy
    session[:user_id] = nil

    head :ok
  end

  def current
    if session[:user_id].present?
      render json: { email: session[:user_id] }
    else
      head :unauthorized
    end
  end

  protected

  def check_params
    error('Back url is missing') && return if params[:back_url].blank?
  end

  def email
    auth_hash[:info][:email] || auth_hash[:info][:emails].first[:value]
  end

  def auth_hash
    request.env['omniauth.auth'].with_indifferent_access
  end

  def log_user_into_couchdb
    master_password = Rails.application.secrets.couchdb_master_password
    auth_session = User.get_auth_session(session[:user_id], master_password)

    cookies['AuthSession'] = auth_session
  end
end
