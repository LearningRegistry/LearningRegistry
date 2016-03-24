require 'test_helper'

# Test for an approval process
class ApprovalsProcessTest < ActiveSupport::TestCase
  include ApprovalTestUtils

  def setup
    approval = ApprovalForm.new(approval_attributes)
    @approval_process = ApprovalProcess.new(approval)
  end

  test '::generate_approval_token' do
    token = @approval_process.generate_approval_token

    token_parts = token.split('.')
    payload = Base64.decode64(token_parts[1])

    assert_equal 3, token_parts.size
    assert_not_nil JSON.parse(payload)['exp']
  end

  test '::generate_delete_token' do
    token = @approval_process.generate_delete_token

    token_parts = token.split('.')
    payload = Base64.decode64(token_parts[1])

    assert_equal 3, token_parts.size
    assert_equal 'delete', JSON.parse(payload)['action']
  end
end
