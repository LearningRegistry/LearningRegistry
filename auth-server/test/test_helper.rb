ENV['RAILS_ENV'] ||= 'test'
require File.expand_path('../../config/environment', __FILE__)
require 'rails/test_help'
require 'minitest/mock'

Dir[Rails.root.join('test/support/**/*')].each { |f| require f }
