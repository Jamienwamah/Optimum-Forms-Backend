import { Model, Document } from 'mongoose';
import { FormFilterParams, FormStatus } from '../types/base-form.types';

export abstract class BaseRepository<T extends Document> {
  constructor(protected readonly model: Model<T>) {}

  async create(payload: Partial<T>): Promise<T> {
    const item = new this.model(payload);
    return await item.save();
  }

  async findWithPagination(filters: FormFilterParams) {
    const query: Record<string, any> = {};
    const page = filters.page || 1;
    const limit = filters.limit || 20;
    const skip = (page - 1) * limit;

    if (filters.status) query.status = filters.status;
    if (filters.employeeId) query['employee.employeeId'] = filters.employeeId;

    const [items, total] = await Promise.all([
      this.model.find(query).sort({ createdAt: -1 }).skip(skip).limit(limit).exec(),
      this.model.countDocuments(query),
    ]);

    return {
      items,
      pagination: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async findById(id: string): Promise<T | null> {
    return await this.model.findById(id).exec();
  }

  async updateOfficialSection(
    id: string,
    officialUseData: Record<string, any>,
    status?: FormStatus
  ): Promise<T | null> {
    const update: Record<string, any> = { officialUse: officialUseData };
    if (status) update.status = status;

    return await this.model
      .findByIdAndUpdate(id, { $set: update }, { new: true, runValidators: true })
      .exec();
  }
}