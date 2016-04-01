require 'test_helper'

# Test for an approval process
class ApprovalsProcessTest < ActiveSupport::TestCase
  include ApprovalTestUtils

  def setup
    @approval_process = ApprovalProcess.new('john@example.org')
  end

  test '::generate_approval_token' do
    @token = @approval_process.generate_approval_token

    assert_valid_payload
    assert_not_nil parsed_payload['exp']
  end

  test '::generate_delete_token' do
    @token = @approval_process.generate_delete_token

    assert_valid_payload
    assert_equal 'delete', parsed_payload['action']
  end

  private

  def token_parts
    @token.split('.')
  end

  def parsed_payload
    JSON.parse(Base64.decode64(token_parts[1]))
  end

  def assert_valid_payload
    assert_equal 3, token_parts.size
    assert_equal 'john@example.org', parsed_payload['email']
  end
end
