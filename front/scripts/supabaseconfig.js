// supabaseConfig.js
const supabaseUrl = process.env.SUPABASEURL;
const supabaseKey = process.env.SUPABASE_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

export default supabase;