require 'test_helper'

class ApprovalMailerTest < ActionMailer::TestCase
  def setup
    @email = ApprovalMailer.confirmation('user@example.org').deliver_now
  end

  test 'confirmation email is queued' do
    assert_not ActionMailer::Base.deliveries.empty?
  end

  test 'from field for confirmation email is correct' do
    assert_equal [Rails.application.secrets.approval_sender], @email.from
  end

  test 'to field for confirmation email is correct' do
    assert_equal ['user@example.org'], @email.to
  end

  test 'subject for confirmation email is correct' do
    assert_equal 'Learning Registry approval confirmation for user@example.org',
                 @email.subject
  end

  test 'body for confirmation email is correct' do
    snippet = /Your account for user@example.org has been successfully approved/

    assert_match snippet, @email.text_part.body.to_s
    assert_match snippet, @email.html_part.body.to_s
  end
end
