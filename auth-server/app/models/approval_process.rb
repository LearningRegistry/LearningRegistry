# Takes care of generating & validating the tokens required for user approval
class ApprovalProcess
  attr_reader :approval

  def initialize(approval)
    @approval = approval
  end

  def generate_approval_token
    payload = { email: approval.email,
                action: 'approve',
                exp: default_expiration }

    JWT.encode(payload, secret, 'HS256')
  end

  def generate_delete_token
    payload = { email: approval.email, action: 'delete' }

    JWT.encode(payload, secret, 'HS256')
  end

  private

  def secret
    Rails.application.secrets.secret_key_base
  end

  def default_expiration
    2.weeks.from_now.to_i
  end
end
