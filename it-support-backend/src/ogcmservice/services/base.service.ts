import { Document } from 'mongoose';
import { BaseRepository } from '../repositories/base.repository';
import { FormFilterParams, FormStatus } from '../types/base-form.types';

export abstract class BaseService<T extends Document> {
  constructor(protected readonly repository: BaseRepository<T>) {}

  async submitForm(payload: Partial<T>): Promise<T> {
    return await this.repository.create(payload);
  }

  async fetchForms(filters: FormFilterParams) {
    return await this.repository.findWithPagination(filters);
  }

  async fetchFormById(id: string): Promise<T | null> {
    return await this.repository.findById(id);
  }

  async processITReview(
    id: string,
    officialUseData: Record<string, any>,
    status?: FormStatus
  ): Promise<T | null> {
    return await this.repository.updateOfficialSection(id, officialUseData, status);
  }
}