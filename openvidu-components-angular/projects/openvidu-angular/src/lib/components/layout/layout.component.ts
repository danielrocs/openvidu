import { ChangeDetectionStrategy, ChangeDetectorRef, Component, ContentChild, OnDestroy, OnInit, TemplateRef } from '@angular/core';
import { Subscription } from 'rxjs';
import { ParticipantService } from '../../services/participant/participant.service';
import { ParticipantAbstractModel } from '../../models/participant.model';
import { LayoutService } from '../../services/layout/layout.service';
import { StreamDirective } from '../../directives/openvidu-angular.directive';

@Component({
	selector: 'ov-layout',
	templateUrl: './layout.component.html',
	styleUrls: ['./layout.component.css'],
	changeDetection: ChangeDetectionStrategy.OnPush
})
export class LayoutComponent implements OnInit, OnDestroy {
	@ContentChild('stream', { read: TemplateRef }) streamTemplate: TemplateRef<any>;

	@ContentChild(StreamDirective)
	set externalStream (externalStream: StreamDirective) {
		// This directive will has value only when STREAM component tagget with '*ovStream' directive
		// is inside of the layout component tagged with '*ovLayout' directive
		if(externalStream) {
			this.streamTemplate = externalStream.template;
		}
	}

	localParticipant: ParticipantAbstractModel;
	remoteParticipants: ParticipantAbstractModel[] = [];
	protected localParticipantSubs: Subscription;
	protected remoteParticipantsSubs: Subscription;

	constructor(protected layoutService: LayoutService, protected participantService: ParticipantService, private cd: ChangeDetectorRef) {}

	ngOnInit(): void {
		this.subscribeToUsers();
		this.layoutService.initialize();
		this.layoutService.update();
	}

	ngOnDestroy() {
		this.localParticipant = null;
		this.remoteParticipants = [];
		if (this.localParticipantSubs) this.localParticipantSubs.unsubscribe();
		if (this.remoteParticipantsSubs) this.remoteParticipantsSubs.unsubscribe();
		this.layoutService.clear();
	}

	protected subscribeToUsers() {
		this.localParticipantSubs = this.participantService.localParticipantObs.subscribe((p) => {
			this.localParticipant = p;
			this.layoutService.update();
			this.cd.markForCheck();
		});

		this.remoteParticipantsSubs = this.participantService.remoteParticipantsObs.subscribe((participants) => {
			this.remoteParticipants = [...participants];
			this.layoutService.update();
			this.cd.markForCheck();
		});
	}
}
