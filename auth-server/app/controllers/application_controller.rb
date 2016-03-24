# Main application controller
class ApplicationController < ActionController::Base
  protect_from_forgery with: :null_session

  def error(message)
    render json: { error: message }, status: :unprocessable_entity
  end
end
