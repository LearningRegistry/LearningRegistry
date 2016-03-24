# Helper class that is responsible for token decoding & verification
class DecodedToken
  attr_reader :token, :decoded_token

  def initialize(token)
    @token = token
    decode
  end

  def email
    payload[:email]
  end

  def valid?
    !@invalid
  end

  def expired?
    !@expired.nil?
  end

  private

  def decode
    @decoded_token = JWT.decode token, secret, true, leeway: 30,
                                                     algorithm: 'HS256'
  rescue JWT::VerificationError
    @invalid = true
  rescue JWT::ExpiredSignature
    @expired = true
  end

  def payload
    decoded_token.first.with_indifferent_access
  end

  def secret
    Rails.application.secrets.secret_key_base
  end
end
