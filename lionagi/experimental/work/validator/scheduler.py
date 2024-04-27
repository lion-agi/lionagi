import asyncio
from collections import defaultdict
from typing import Dict, Optional

from ..record.form import Form
from ..record.report import Report
from .validator import Validator


class Scheduler:
    """Manages the lifecycle and processing of tasks, reports, and forms."""
    
    def __init__(self):
        self.reports: Dict[str, Report] = {}
        self.task_queue = asyncio.Queue()
    
    async def receive_task(self, data: Dict):
        """Validate and enqueue tasks for processing."""
        if await Validator.validate(data):
            if data['report_id'] not in self.reports:
                self.reports[data['report_id']] = Report(data['report_id'])
            report = self.reports[data['report_id']]
            form = Form(data['form_id'])
            report.add_form(form)
            await self.task_queue.put((form, data))
            print(f"Received and validated task for Report ID: {data['report_id']}")
        else:
            print("Task validation failed.")

    async def process_tasks(self):
        """Continuously processes tasks from the queue."""
        while True:
            form, data = await self.task_queue.get()
            try:
                # Simulate form processing, which would typically be done by a WorkFunction
                await self.process_form(form, data)
                self.task_queue.task_done()
                print(f"Processed task for Form ID: {form.form_id}")
            except Exception as e:
                print(f"Error processing task for Form ID: {form.form_id}: {str(e)}")

    async def process_form(self, form: Form, data: Dict):
        """Processes a form, potentially simulating work function logic."""
        await asyncio.sleep(1)  # Simulate work delay
        form.complete_form()  # Mark the form as completed after the 'work' is done

        # Check if the entire report is complete and update accordingly
        report = self.reports[data['report_id']]
        if report.is_complete():
            print(f"Report {report.report_id} completed.")
    
    def run(self):
        """Starts the scheduler to process tasks."""
        try:
            asyncio.run(self.process_tasks())
        except KeyboardInterrupt:
            print("Scheduler shutdown.")

# Example of setting up and running the scheduler
scheduler = Scheduler()
asyncio.run(scheduler.receive_task({
    'report_id': '001',
    'form_id': '001A',
    'required_field': 'data'
}))
scheduler.run()
