import { Schema } from 'mongoose';

export const baseEmployeeSchema = new Schema(
  {
    name: { type: String, required: true },
    department: { type: String, required: true },
    jobTitle: { type: String, required: true },
    employeeId: { type: String, required: true, index: true },
  },
  { _id: false }
);

export const baseFormFields = {
  status: {
    type: String,
    enum: ['pending', 'under-review', 'approved', 'rejected', 'completed'],
    default: 'pending',
    index: true,
  },
  employee: { type: baseEmployeeSchema, required: true },
  officialUse: { type: Schema.Types.Mixed, default: {} },
};