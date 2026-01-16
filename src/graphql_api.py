"""
GraphQL API

Provides GraphQL endpoint for flexible data querying.
"""

import logging

import graphene
from flask_graphql import GraphQLView
from graphene import relay

logger = logging.getLogger("dms.graphql")


# GraphQL Types


class ServiceType(graphene.ObjectType):
    """Service GraphQL type."""

    class Meta:
        interfaces = (relay.Node,)

    id = graphene.ID()
    service_name = graphene.String()
    region = graphene.String()
    target_group = graphene.String()
    brutto_rate = graphene.Float()
    netto_rate = graphene.Float()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()


class UserType(graphene.ObjectType):
    """User GraphQL type."""

    class Meta:
        interfaces = (relay.Node,)

    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()
    role = graphene.String()
    is_active = graphene.Boolean()
    created_at = graphene.DateTime()


class StatisticsType(graphene.ObjectType):
    """Statistics GraphQL type."""

    total_services = graphene.Int()
    avg_brutto_rate = graphene.Float()
    total_users = graphene.Int()
    services_by_region = graphene.JSONString()


# Queries


class Query(graphene.ObjectType):
    """GraphQL queries."""

    # Node interface
    node = relay.Node.Field()

    # Service queries
    service = graphene.Field(ServiceType, id=graphene.ID(required=True))
    services = graphene.List(
        ServiceType,
        region=graphene.String(),
        limit=graphene.Int(default_value=100),
        offset=graphene.Int(default_value=0),
    )

    # User queries
    user = graphene.Field(UserType, id=graphene.ID(required=True))
    users = graphene.List(UserType, limit=graphene.Int(default_value=100))

    # Statistics
    statistics = graphene.Field(StatisticsType)

    def resolve_service(self, info, id):
        """Get single service by ID."""
        from src.core.database import Database

        db = Database()
        service = db.get_service(int(id))

        if not service:
            return None

        return ServiceType(
            id=service.id,
            service_name=service.basic_info.service_name,
            region=service.basic_info.region,
            target_group=service.basic_info.target_group,
            brutto_rate=service.financial.brutto_rate,
            netto_rate=getattr(service.financial, "netto_rate", 0),
            created_at=service.created_at,
            updated_at=service.updated_at,
        )

    def resolve_services(self, info, region=None, limit=100, offset=0):
        """Get list of services with filters."""
        from src.core.database import Database

        db = Database()
        services = db.list_services()

        # Filter by region
        if region:
            services = [s for s in services if s.basic_info.region == region]

        # Pagination
        services = services[offset : offset + limit]

        return [
            ServiceType(
                id=s.id,
                service_name=s.basic_info.service_name,
                region=s.basic_info.region,
                target_group=s.basic_info.target_group,
                brutto_rate=s.financial.brutto_rate,
                netto_rate=getattr(s.financial, "netto_rate", 0),
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in services
        ]

    def resolve_statistics(self, info):
        """Get system statistics."""
        from src.core.database import Database

        db = Database()
        services = db.list_services()

        total = len(services)
        avg_rate = sum(s.financial.brutto_rate for s in services) / total if total > 0 else 0

        # By region
        by_region = {}
        for s in services:
            region = s.basic_info.region
            by_region[region] = by_region.get(region, 0) + 1

        return StatisticsType(
            total_services=total,
            avg_brutto_rate=round(avg_rate, 2),
            total_users=0,  # Placeholder
            services_by_region=by_region,
        )


# Mutations


class CreateService(graphene.Mutation):
    """Create new service mutation."""

    class Arguments:
        service_name = graphene.String(required=True)
        region = graphene.String(required=True)
        target_group = graphene.String()
        brutto_rate = graphene.Float()

    service = graphene.Field(ServiceType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, service_name, region, target_group=None, brutto_rate=0):
        """Create service."""
        from src.core.database import Database
        from src.models.service import Service

        try:
            service = Service()
            service.basic_info.service_name = service_name
            service.basic_info.region = region
            service.basic_info.target_group = target_group or ""
            service.financial.brutto_rate = brutto_rate

            db = Database()
            service_id = db.save_service(service)
            service.id = service_id

            logger.info(f"Service created via GraphQL: {service_id}")

            return CreateService(
                service=ServiceType(
                    id=service_id,
                    service_name=service_name,
                    region=region,
                    target_group=target_group,
                    brutto_rate=brutto_rate,
                ),
                success=True,
                message="Service created successfully",
            )

        except Exception as e:
            logger.error(f"Error creating service: {e}")
            return CreateService(service=None, success=False, message=str(e))


class UpdateService(graphene.Mutation):
    """Update service mutation."""

    class Arguments:
        id = graphene.ID(required=True)
        service_name = graphene.String()
        region = graphene.String()
        target_group = graphene.String()
        brutto_rate = graphene.Float()

    service = graphene.Field(ServiceType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, **kwargs):
        """Update service."""
        from src.core.database import Database

        try:
            db = Database()
            service = db.get_service(int(id))

            if not service:
                return UpdateService(service=None, success=False, message="Service not found")

            # Update fields
            if "service_name" in kwargs:
                service.basic_info.service_name = kwargs["service_name"]
            if "region" in kwargs:
                service.basic_info.region = kwargs["region"]
            if "target_group" in kwargs:
                service.basic_info.target_group = kwargs["target_group"]
            if "brutto_rate" in kwargs:
                service.financial.brutto_rate = kwargs["brutto_rate"]

            db.save_service(service)

            logger.info(f"Service updated via GraphQL: {id}")

            return UpdateService(
                service=ServiceType(
                    id=service.id,
                    service_name=service.basic_info.service_name,
                    region=service.basic_info.region,
                    target_group=service.basic_info.target_group,
                    brutto_rate=service.financial.brutto_rate,
                ),
                success=True,
                message="Service updated successfully",
            )

        except Exception as e:
            logger.error(f"Error updating service: {e}")
            return UpdateService(service=None, success=False, message=str(e))


class Mutation(graphene.ObjectType):
    """GraphQL mutations."""

    create_service = CreateService.Field()
    update_service = UpdateService.Field()


# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)


# Flask view
def create_graphql_view():
    """Create GraphQL view for Flask."""
    return GraphQLView.as_view("graphql", schema=schema, graphiql=True)  # Enable GraphiQL interface
