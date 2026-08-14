generic-form.controller.tsimport mongoose from 'mongoose';

export const connectDatabase = async (): Promise<void> => {
  try {
    const uri = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/it_support_db';
    await mongoose.connect(uri);
    console.log('[Database] Connected successfully to MongoDB');
  } catch (error) {
    console.error('[Database] Connection error:', error);
    process.exit(1);
  }
};