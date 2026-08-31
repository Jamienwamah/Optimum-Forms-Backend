export type FormStatus = 'pending' | 'under-review' | 'approved' | 'rejected' | 'completed';

export interface BaseEmployeeMeta {
  name: string;
  department: string;
  jobTitle: string;
  employeeId: string;
}

export interface IBaseForm {
  status: FormStatus;
  employee: BaseEmployeeMeta;
  officialUse?: Record<string, any>;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface FormFilterParams {
  status?: FormStatus;
  employeeId?: string;
  limit?: number;
  page?: number;
}