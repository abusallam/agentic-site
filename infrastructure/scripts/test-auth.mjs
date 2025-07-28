import { supabase } from '../lib/supabase.js';

async function testAuth() {
  const email = `testuser-${Date.now()}@example.com`;
  const password = 'TestPassword123';

  console.log(`Attempting to sign up with email: ${email}`);
  const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
    email,
    password,
  });

  if (signUpError) {
    console.error('Sign up failed:', signUpError.message);
    return;
  }

  console.log('Sign up successful:', signUpData);

  console.log('Attempting to sign in...');
  const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (signInError) {
    console.error('Sign in failed:', signInError.message);
    return;
  }

  console.log('Sign in successful:', signInData);
}

testAuth();
