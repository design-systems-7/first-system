import datetime
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.crud.order import OrderCRUD
from app.core.issue_order_service.complete_order_service import CompleteOrderService

from app.schemas.order import AssignedOrder, assigned_order_from_order


class IssueOrderService:
    """A class that handles issuing of order to executer."""
    def __init__(self,
                 order_completion_service: CompleteOrderService) -> None:
        self.order_completion_service = order_completion_service

    async def issue_order_for_execution(self, session: AsyncSession,
                                        executer_id: uuid.UUID,
                                        last_taken_order_id: Optional[uuid.UUID]) -> Optional[AssignedOrder]:
        if last_taken_order_id:
            await self.order_completion_service.mark_order_as_complete(session=session, order_id=last_taken_order_id)

        crud_order: OrderCRUD = OrderCRUD(session)
        # check if already issued order for execution, but executer lost it
        issued_order = await crud_order.check_for_issued_order(executer_id=executer_id)
        if issued_order:
            return assigned_order_from_order(issued_order)

        new_order = await crud_order.get_active_order_for_execution(executer_id=executer_id)
        if new_order:
            acquire_time = datetime.datetime.now()
            await crud_order.take_order(assigned_order_id=new_order.assigned_order_id,
                                        acquire_time=acquire_time)
            return assigned_order_from_order(new_order)

        return None

    async def issue_order_for_update_check(self, session: AsyncSession, order_id: uuid.UUID) -> Optional[AssignedOrder]:
        crud_order: OrderCRUD = OrderCRUD(session)
        updated_order = await crud_order.get_issued_order(order_id=order_id)
        if updated_order:
            return assigned_order_from_order(updated_order)
        return None


issue_order_service = IssueOrderService(order_completion_service=CompleteOrderService())
