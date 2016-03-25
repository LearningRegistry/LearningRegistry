# Main controller for approval requests
class ApprovalsController < ApplicationController
  before_action :set_approval_values, only: :create
  before_action :set_decoded_token, only: %i(confirm delete)

  def new
    @approval = ApprovalForm.new
  end

  def create
    if @approval.deliver
      session[:authenticated_email] = nil

      redirect_to new_approval_url,
                  notice: 'Your approval request has been sent successfully'
    else
      render :new
    end
  end

  def confirm
    error('Signature validation failed') && return unless @decoded_token.valid?
    error('Approval has already expired') && return if @decoded_token.expired?

    if User.create(user_attributes)
      success('Approval has been successfully confirmed ')
    else
      error('User could not be created')
    end
  end

  def delete
    if @decoded_token.valid?
      User.find_by_name(@decoded_token.email).destroy

      success('User has been successfully deleted')
    else
      error('Signature validation failed')
    end
  end

  private

  def set_approval_values
    @approval = ApprovalForm.new(params[:approval_form])
    @approval.request = request
    @approval.authenticated_email = session[:authenticated_email]
    @approval.approval_link = confirm_approvals_url(
      token: approval_process.generate_approval_token
    )
    @approval.delete_link = delete_approvals_url(
      token: approval_process.generate_delete_token
    )
  end

  def set_decoded_token
    @decoded_token = DecodedToken.new(params[:token])
  end

  def approval_process
    @approval_process ||= ApprovalProcess.new(@approval)
  end

  def user_attributes
    {
      id: "org.couchdb.user:#{@decoded_token.email}",
      name: @decoded_token.email,
      oauth: { consumer_keys: { @decoded_token.email => SecureRandom.hex },
               tokens: { node_sign_token: SecureRandom.hex } }
    }
  end
end
