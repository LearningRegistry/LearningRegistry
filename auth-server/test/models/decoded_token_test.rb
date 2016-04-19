require 'test_helper'

# Test for a decoded token
class DecodedTokenTest < ActiveSupport::TestCase
  include ApprovalTestUtils

  def setup
    @decoded_token = DecodedToken.new(valid_token)
  end

  test '::email' do
    assert_equal 'me@example.org', @decoded_token.email
  end

  test '::valid?' do
    invalid_decoded_token = DecodedToken.new(invalid_token)

    assert_equal true, @decoded_token.valid?
    assert_equal false, invalid_decoded_token.valid?
  end

  test '::expired?' do
    expired_decoded_token = DecodedToken.new(expired_token)

    assert_equal false, @decoded_token.expired?
    assert_equal true, expired_decoded_token.expired?
  end
end
